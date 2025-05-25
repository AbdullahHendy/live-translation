/*
* Live Translation Go Client
*
* This program captures raw PCM audio from the system microphone and streams it to a WebSocket server
* for real-time transcription and translation.
*
* Server-side expectations:
* - Format:       Raw PCM
* - Sample Rate:  16,000 Hz
* - Channels:     Mono (1 channel)
* - Bit Depth:    16-bit (signed int16) → 2 bytes per sample
* - Chunk Size:   512 samples of 16-bit mono audio (1024 bytes)
*
* Audio is buffered and transmitted in fixed-size 512-sample chunks, matching exactly what the server expects.
* Uses malgo (miniaudio) for cross-platform microphone input, and gorilla/websocket for client-server communication.
* Inspired by the malgo example: https://github.com/gen2brain/malgo/blob/master/_examples/capture/capture.go
 */

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"

	"github.com/gen2brain/malgo"
	"github.com/gorilla/websocket"
)

const (
	serverURL    = "ws://localhost:8765"
	sampleRate   = 16000
	channels     = 1
	format       = malgo.FormatS16
	sampleSize   = 2 // 16-bit int
	chunkSamples = 512
)

func main() {
	// Graceful shutdown signal
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, os.Interrupt)

	// Connect to WebSocket
	fmt.Println("🔌 Connecting to WebSocket server...")
	conn, _, err := websocket.DefaultDialer.Dial(serverURL, nil)
	if err != nil {
		log.Fatalf("WebSocket error: %v", err)
	}
	defer conn.Close()
	fmt.Println("✅ Connected to", serverURL)

	// Handle server responses
	go func() {
		for {
			_, message, err := conn.ReadMessage()
			if err != nil {
				log.Printf("❌ WebSocket read error: %v", err)
				return
			}

			var response struct {
				Transcription string `json:"transcription"`
				Translation   string `json:"translation"`
			}
			if err := json.Unmarshal(message, &response); err != nil {
				log.Printf("⚠️ JSON parse error: %v", err)
				continue
			}

			if response.Transcription != "" {
				fmt.Println("📝", response.Transcription)
			}
			if response.Translation != "" {
				fmt.Println("🌍", response.Translation)
			}
		}
	}()

	// Init malgo context
	// Source: https://github.com/gen2brain/malgo/blob/master/_examples/capture/capture.go
	ctx, err := malgo.InitContext(nil, malgo.ContextConfig{}, nil)
	if err != nil {
		log.Fatalf("malgo context error: %v", err)
	}
	defer func() {
		_ = ctx.Uninit()
		ctx.Free()
	}()

	deviceConfig := malgo.DefaultDeviceConfig(malgo.Capture)
	deviceConfig.Capture.Format = format
	deviceConfig.Capture.Channels = channels
	deviceConfig.SampleRate = sampleRate
	deviceConfig.Alsa.NoMMap = 1 // Important for Linux stability

	sampleBytes := uint32(malgo.SampleSizeInBytes(format))
	chunkSizeBytes := chunkSamples * sampleBytes
	buffer := make([]byte, 0, chunkSizeBytes*2) // Arbitrary safe starting size

	// mic data callback
	onRecv := func(_, inputSample []byte, frameCount uint32) {
		buffer = append(buffer, inputSample...)

		for uint32(len(buffer)) >= chunkSizeBytes {
			chunk := buffer[:chunkSizeBytes]
			buffer = buffer[chunkSizeBytes:]

			err := conn.WriteMessage(websocket.BinaryMessage, chunk)
			if err != nil {
				log.Printf("❌ Failed to send chunk: %v", err)
			}
		}
	}

	deviceCallbacks := malgo.DeviceCallbacks{Data: onRecv}

	// Init and start capture device
	device, err := malgo.InitDevice(ctx.Context, deviceConfig, deviceCallbacks)
	if err != nil {
		log.Fatalf("malgo InitDevice failed: %v", err)
	}
	defer device.Uninit()

	if err := device.Start(); err != nil {
		log.Fatalf("failed to start device: %v", err)
	}

	fmt.Println("🎤 Recording... Press Ctrl+C to stop.")
	<-sig
	fmt.Println("🛑 Stopping capture...")
	_ = device.Stop()
}
