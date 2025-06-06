/**
 * Live Translation Node.js Client
 *
 * This script captures raw PCM audio from the system microphone, encodes it using Opus,
 * and streams the compressed packets to a WebSocket server for real-time transcription
 * and translation.
 *
 * Server-side expectations:
 * - Receives Opus-encoded audio with the following original characteristics:
 *   - Sample Rate:  16,000 Hz
 *   - Channels:     Mono (1 channel)
 *   - Bit Depth:    16-bit (signed int16) → 2 bytes per sample
 *   - Frame Size:   640 samples (40 ms) per encoded packet
 *
 * Audio is buffered into 1280-byte (640-sample) chunks, encoded using @discordjs/opus,
 * and streamed to the server via WebSocket.
 * Uses node-record-lpcm16 for microphone input and ws for WebSocket communication.
 */

const WebSocket = require('ws');
const record = require('node-record-lpcm16');
const OpusEncoder = require('@discordjs/opus').OpusEncoder;

// --- CONFIG ---
const SERVER_URI = 'ws://localhost:8765';
const SAMPLE_RATE = 16000;
const CHANNELS = 1;
const CHUNK_SIZE_BYTES = 640 * 2; // 640 samples @ 16-bit mono

// --- CONNECT TO SERVER ---
const ws = new WebSocket(SERVER_URI);


// --- OPUS ENCODER ---
const encoder = new OpusEncoder(SAMPLE_RATE, CHANNELS);
encoder.setBitrate(30000);

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

        // Send full 1280-byte chunks to the server
        while (buffer.length >= CHUNK_SIZE_BYTES) {
            const slice = buffer.subarray(0, CHUNK_SIZE_BYTES);

            // Encode the slice to Opus format
            try {
                const encoded = encoder.encode(slice);
                ws.send(encoded);
            } catch (err) {
                console.error('❌ Opus encoding error:', err);
            }

            buffer = buffer.subarray(CHUNK_SIZE_BYTES);
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
