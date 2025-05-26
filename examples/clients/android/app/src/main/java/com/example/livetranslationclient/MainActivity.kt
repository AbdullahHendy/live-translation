package com.example.livetranslationclient

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Color
import android.media.*
import android.os.Bundle
import android.text.Spannable
import android.text.SpannableString
import android.text.style.ForegroundColorSpan
import android.util.Log
import android.widget.Button
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.RequiresPermission
import androidx.core.content.ContextCompat
import okhttp3.*
import okio.ByteString.Companion.toByteString
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * Live Translation Kotlin/Android Client
 *
 * This activity captures raw microphone audio using Android's AudioRecord API
 * and streams it to a WebSocket server for real-time transcription and translation.
 *
 * Server-side expectations:
 * - Format:       Raw PCM
 * - Sample Rate:  16,000 Hz
 * - Channels:     Mono (1 channel)
 * - Bit Depth:    16-bit (signed int16) → 2 bytes per sample
 * - Chunk Size:   512 samples → 1024 bytes (512 × 2 bytes)
 *
 * Audio is captured and streamed in 1024-byte chunks, precisely matching the server's format.
 * Uses OkHttp's WebSocket client for lightweight and efficient real-time streaming.
 */

class MainActivity : ComponentActivity() {

    companion object {
        private const val TAG = "LiveTranslationClient"
        private const val SAMPLE_RATE = 16000
        private const val CHUNK_SIZE = 512
        private const val CHUNK_SIZE_BYTES = CHUNK_SIZE * 2
        private const val WEBSOCKET_URL = "ws://192.168.1.1:8765" // localhost doesn't work on emulators, use host IP.
    }

    private lateinit var audioRecord: AudioRecord
    private var isRecording = false
    private var webSocket: WebSocket? = null
    private lateinit var micPermissionLauncher: ActivityResultLauncher<String>

    // UI components
    private lateinit var startButton: Button
    private lateinit var stopButton: Button
    private lateinit var textOutput: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Link UI elements
        startButton = findViewById(R.id.startButton)
        stopButton = findViewById(R.id.stopButton)
        textOutput = findViewById(R.id.textOutput)

        // Register permission request handler
        micPermissionLauncher = registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { isGranted ->
            if (isGranted) {
                tryStartStreaming()
            } else {
                Log.e(TAG, "Microphone permission denied")
                appendLog("Microphone permission denied", Color.RED)
            }
        }

        // Set button click listener to request mic permission
        startButton.setOnClickListener {
            micPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }

        stopButton.setOnClickListener {
            stopStreaming()
        }
    }

    private fun tryStartStreaming() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            == PackageManager.PERMISSION_GRANTED
        ) {
            startStreaming()
        } else {
            Log.e(TAG, "Permission supposedly granted but check failed")
            appendLog("Permission check failed", Color.RED)
        }
    }

    @RequiresPermission(Manifest.permission.RECORD_AUDIO)
    private fun startStreaming() {
        // Disable the button once streaming starts
        runOnUiThread {
            startButton.isEnabled = false
        }

        val bufferSize = AudioRecord.getMinBufferSize(
            SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        )

        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            bufferSize
        )

        val client = OkHttpClient.Builder()
            .readTimeout(0, TimeUnit.MILLISECONDS)
            .build()

        val request = Request.Builder()
            .url(WEBSOCKET_URL)
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val json = JSONObject(text)
                val transcription = json.optString("transcription")
                val translation = json.optString("translation")

                if (transcription.isNotBlank()) {
                    Log.d(TAG, "Transcription: $transcription")
                    appendLog("Transcription: $transcription", Color.BLACK)
                }

                if (translation.isNotBlank()) {
                    Log.d(TAG, "Translation: $translation")
                    appendLog("Translation: $translation", Color.RED)
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "WebSocket error", t)
                appendLog("WebSocket error: ${t.message}", Color.RED)
            }
        })

        // Start audio streaming thread
        val thread = Thread {
            val chunk = ByteArray(CHUNK_SIZE_BYTES)
            isRecording = true
            audioRecord.startRecording()
            Log.d(TAG, "Recording started")
            appendLog("Recording started", Color.DKGRAY)

            while (isRecording) {
                val read = audioRecord.read(chunk, 0, CHUNK_SIZE_BYTES)
                if (read == CHUNK_SIZE_BYTES) {
                    webSocket?.send(chunk.toByteString(0, CHUNK_SIZE_BYTES))
                }
            }

            audioRecord.stop()
            audioRecord.release()
            Log.d(TAG, "Recording stopped")
            appendLog("Recording stopped", Color.DKGRAY)
        }

        thread.start()
    }

    private fun appendLog(message: String, color: Int) {
        runOnUiThread {
            val spannable = SpannableString("$message\n")
            spannable.setSpan(
                ForegroundColorSpan(color),
                0,
                spannable.length,
                Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
            )
            textOutput.append(spannable)
        }
    }

    private fun stopStreaming() {
        runOnUiThread {
            stopButton.isEnabled = false
            startButton.isEnabled = true
        }

        isRecording = false
        webSocket?.close(1000, "User stopped")
        appendLog("Streaming stopped by user", Color.DKGRAY)
        Log.d(TAG, "Streaming manually stopped")
    }

    override fun onDestroy() {
        super.onDestroy()
        stopStreaming()
    }
}
