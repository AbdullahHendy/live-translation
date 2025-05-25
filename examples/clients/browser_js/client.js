/**
 * Live Translation Web browser Client
 *
 * This script captures raw audio from the microphone and streams it to a WebSocket server
 * for real-time transcription and translation.
 *
 * Server-side expectations:
 * - Format:       Raw PCM
 * - Sample Rate:  16,000 Hz
 * - Channels:     Mono (1 channel)
 * - Bit Depth:    16-bit (signed int16) → 2 bytes per sample
 * - Chunk Size:   512 samples of 16-bit mono audio
 *
 * Audio is buffered and sent in 512-sample chunks of 16-bit signed integers, exactly matching what the server's expects.
 * Uses Web Audio API + WebSocket for broad compatibility.
 * Note: This script requires a Web Audio Worklet processor to handle PCM audio.
 */

const WS_URL = 'ws://localhost:8765';
const SAMPLE_RATE = 16000;
const CHUNK_SIZE = 512;

const log = (msg) => {
    document.getElementById('output').textContent += msg + '\n';
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

document.getElementById('start').onclick = async () => {
    const startBtn = document.getElementById('start');
    const stopBtn = document.getElementById('stop');
    const status = document.getElementById('status');

    startBtn.disabled = true;
    stopBtn.disabled = false;
    status.textContent = '⏳ Connecting...';

    try {
        ws = new WebSocket(WS_URL);
        await new Promise((res, rej) => {
            ws.onopen = res;
            ws.onerror = () => rej(new Error('WebSocket connection failed'));
        });

        status.textContent = '✅ Connected';
        log('✅ WebSocket connected');

        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        context = new AudioContext({ sampleRate: SAMPLE_RATE });
        log(`🎧 AudioContext sample rate: ${context.sampleRate}`);
        log(`--------------------------------------------`)
        log(`--------------------------------------------`)

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

            while (buffer.length >= CHUNK_SIZE) {
                const chunk = new Int16Array(buffer.slice(0, CHUNK_SIZE));
                ws.send(new Uint8Array(chunk.buffer));
                buffer = buffer.slice(CHUNK_SIZE);
            }
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.transcription) log('📝 ' + msg.transcription);
                if (msg.translation) log('🌍 ' + msg.translation);
            } catch {
                log('❌ Failed to parse message');
            }
        };

    } catch (err) {
        status.textContent = '❌ Failed to connect';
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
    document.getElementById('status').textContent = '';
    log(`--------------------------------------------`)
    log(`--------------------------------------------`)
    log('🛑 Stopped');
    log(`--------------------------------------------`)
    log(`--------------------------------------------`)
};
