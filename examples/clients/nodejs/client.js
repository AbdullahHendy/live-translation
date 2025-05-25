/**
 * Live Translation Node.js Client
 *
 * This script captures raw audio from the microphone and streams it to a WebSocket server
 * for real-time transcription and translation.
 *
 * Server-side expectations:
 * - Format:       Raw PCM
 * - Sample Rate:  16,000 Hz
 * - Channels:     Mono (1 channel)
 * - Bit Depth:    16-bit (signed int16) → 2 bytes per sample
 * - Chunk Size:   512 samples → 1024 bytes (512 × 2 bytes)
 *
 * Audio is buffered and sent in 1024-byte slices, exactly matching what the server's expects.
 * Uses node-record-lpcm16 + ws for broad compatibility.
 */

const WebSocket = require('ws');
const record = require('node-record-lpcm16');

// --- CONFIG ---
const SERVER_URI = 'ws://localhost:8765';
const SAMPLE_RATE = 16000;
const CHUNK_SIZE_BYTES = 512 * 2; // 512 samples @ 16-bit mono

// --- CONNECT TO SERVER ---
const ws = new WebSocket(SERVER_URI);

ws.on('open', () => {
    console.log('🎤 Connected to live-translation server');
    console.log(`🎤 Recording audio at ${SAMPLE_RATE} Hz, sending ${CHUNK_SIZE_BYTES} bytes per chunk`);
    console.log(`--------------------------------------------`);
    console.log(`--------------------------------------------`);
    // Start recording raw PCM audio from default mic
    const mic = record
        .record({
            sampleRate: SAMPLE_RATE,
            channels: 1,
            audioType: 'raw',
            endOnSilence: false,
            recorder: 'sox',
        })
        .stream();

    // Buffer for accumulating partial audio data
    let buffer = Buffer.alloc(0);

    mic.on('data', (chunk) => {
        if (!chunk || chunk.length === 0) return;

        // Append new chunk to buffer
        buffer = Buffer.concat([buffer, chunk]);

        // Send full 1024-byte chunks to the server
        while (buffer.length >= CHUNK_SIZE_BYTES) {
            const slice = buffer.subarray(0, CHUNK_SIZE_BYTES);
            buffer = buffer.subarray(CHUNK_SIZE_BYTES);
            ws.send(slice);
        }
    });

    mic.on('error', (err) => {
        console.error('🎤 Mic error:', err);
    });

    process.on('SIGINT', () => {
        console.log('\n🛑 Ctrl+C detected. Stopping...');
        mic.pause();
        ws.close();
        process.exit(0);
    });
});

// --- SERVER RESPONSES ---
ws.on('message', (data) => {
    try {
        const msg = JSON.parse(data);
        if (msg.transcription) console.log('📝', msg.transcription);
        if (msg.translation) console.log('🌍', msg.translation);
    } catch (err) {
        console.error('❌ Failed to parse server message:', err);
    }
});

ws.on('close', () => {
    console.log('🔌 WebSocket connection closed');
});

ws.on('error', (err) => {
    console.error('❗ WebSocket error:', err);
});
