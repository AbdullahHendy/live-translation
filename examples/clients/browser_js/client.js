/**
 * Live Translation Web browser Client
 *
 * This script captures raw audio from the microphone, encodes it using Opus, and streams it to a WebSocket server
 * for real-time transcription and translation.
 *
 * Server-side expectations:
 * - Receives Opus-encoded audio with the following original characteristics:
 *   - Sample Rate:  16,000 Hz
 *   - Channels:     Mono (1 channel)
 *   - Bit Depth:    16-bit (signed int16) → 2 bytes per sample
 *   - Frame Size:   640 samples (40 ms) per encoded packet
 *
 * Audio is captured as 16-bit PCM, encoded using libopus.wasm in-browser, and sent as compressed Opus packets.
 * Uses Web Audio API + WebSocket for broad compatibility.
 * Note: This script requires a Web Audio Worklet processor to handle float32 PCM audio from the microphone.
 */

const WS_URL = 'ws://localhost:8765';
const SAMPLE_RATE = 16000;
const CHANNELS = 1;
const CHUNK_SIZE = 640;
const CHUNK_SIZE_MS = (CHUNK_SIZE / SAMPLE_RATE) * 1000; // 40 ms
const OPUS_BITRATE = 30000;
const APPLICATION_VOIP = true;

const log = (msg) => {
    const logDiv = document.getElementById('log-content');
    logDiv.textContent += msg + '\n';
    logDiv.scrollTop = logDiv.scrollHeight;
};

// Downsample buffer from inputRate to targetRate
function downsampleBuffer(buffer, inputRate, targetRate) {
    if (inputRate === targetRate) return buffer;
    const ratio = inputRate / targetRate;
    const newLength = Math.round(buffer.length / ratio);
    const result = new Float32Array(newLength);
    let offset = 0;
    for (let i = 0; i < newLength; i++) {
        const nextOffset = Math.round((i + 1) * ratio);
        let sum = 0, count = 0;
        for (let j = offset; j < nextOffset && j < buffer.length; j++) {
            sum += buffer[j];
            count++;
        }
        result[i] = sum / count;
        offset = nextOffset;
    }
    return result;
}

let ws = null, context = null, node = null, stream = null, buffer = [];
let encoder = null
libopus.onload = () => {
    encoder = new libopus.Encoder(CHANNELS, SAMPLE_RATE, OPUS_BITRATE, CHUNK_SIZE_MS, APPLICATION_VOIP);
};

document.getElementById('start').onclick = async () => {
    const startBtn = document.getElementById('start');
    const stopBtn = document.getElementById('stop');

    startBtn.disabled = true;
    stopBtn.disabled = false;
    log('⏳ Connecting...');

    try {
        ws = new WebSocket(WS_URL);
        await new Promise((res, rej) => {
            ws.onopen = res;
            ws.onerror = () => rej(new Error('WebSocket connection failed'));
        });

        log('✅ Connected');

        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        context = new AudioContext({ sampleRate: SAMPLE_RATE });
        log(`🎤 AudioContext sample rate: ${context.sampleRate}`);

        await context.audioWorklet.addModule('worklet-processor.js');
        node = new AudioWorkletNode(context, 'pcm-processor');

        const source = context.createMediaStreamSource(stream);
        source.connect(node);
        node.connect(context.destination);

        node.port.onmessage = (event) => {
            const floatSamples = event.data;
            // Although SAMPLE_RATE is passed to the AudioContext, effectively making the downsampleBuffer function unnecessary,
            // we keep it here to ensure compatibility with older platforms where the sample rate parameter might not be respected.
            const downsampled = downsampleBuffer(floatSamples, context.sampleRate, SAMPLE_RATE);
            const int16 = new Int16Array(downsampled.length);
            // Convert float samples to 16-bit signed integers
            for (let i = 0; i < downsampled.length; i++) {
                int16[i] = Math.max(-1, Math.min(1, downsampled[i])) * 0x7fff;
            }

            buffer.push(...int16);

            // Encode and stream CHUNK_SIZE-sample chunks
            while (buffer.length >= CHUNK_SIZE) {
                const chunk = new Int16Array(buffer.slice(0, CHUNK_SIZE));

                // Encoding and sending the chunk - start
                encoder.input(chunk);
                let encoded = encoder.output();
                if (encoded) {
                    // Send the encoded chunk to the server
                    ws.send(encoded);
                } else {
                    log('❌ Encoder output is empty');
                }
                // Encoding and sending the chunk - end

                // Remove the processed chunk from the buffer
                buffer = buffer.slice(CHUNK_SIZE);
            }
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.transcription || msg.translation) {
                    document.getElementById('transcription').textContent = msg.transcription;
                    document.getElementById('translation').textContent = msg.translation; 
                }
            } catch {
                log('❌ Failed to parse message');
            }
        };

    } catch (err) {
        log('❌ Failed to connect');
        log(err.message);
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
};

document.getElementById('stop').onclick = () => {
    if (node) node.disconnect();
    if (context) context.close();
    if (stream) stream.getTracks().forEach(t => t.stop());
    if (ws) ws.close();

    document.getElementById('start').disabled = false;
    document.getElementById('stop').disabled = true;
    log('🛑 Stopped');
    log(`--------------------------------------------`)
};
