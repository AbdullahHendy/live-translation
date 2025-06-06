/**
 * Live Translation C# Client
 *
 * This program captures raw PCM audio from the system microphone, encodes it
 * using Opus (via Concentus), and streams it to a WebSocket server for real-time
 * transcription and translation.
 *
 * Server-side expectations:
 * - Receives Opus-encoded audio with the following original characteristics:
 *   - Sample Rate:  16,000 Hz
 *   - Channels:     Mono (1 channel)
 *   - Bit Depth:    16-bit (signed int16) → 2 bytes per sample
 *   - Frame Size:   640 samples (40 ms) per encoded packet
 *
 * Audio is captured in 640-sample chunks as raw PCM (16-bit, mono, 16kHz),
 * encoded to Opus using Concentus, and transmitted as compressed Opus packets.
 * Uses PortAudioSharp2 for cross-platform microphone input,
 * and WebSocketSharp for client-server communication.
 */

using System.Runtime.InteropServices;
using PortAudioSharp;
using WebSocketSharp;
using Concentus;
using Concentus.Enums;

class Program
{
    const int SampleRate = 16000;
    const int Channels = 1;
    const int ChunkSamples = 640;
    const int ChunkBytes = ChunkSamples * 2;

    static byte[] buffer = new byte[ChunkBytes * 2];  // Initial safe size for buffering audio
    static int filled = 0;
    static WebSocket? ws;

    static void Main()
    {
        Console.WriteLine("🔌 Connecting to WebSocket...");
        ws = new WebSocket("ws://localhost:8765");
        ws.OnMessage += (sender, e) =>
        {
            try
            {
                var json = System.Text.Json.JsonDocument.Parse(e.RawData);
                if (json.RootElement.TryGetProperty("transcription", out var t))
                    Console.WriteLine("📝 " + t.GetString());
                if (json.RootElement.TryGetProperty("translation", out var tr))
                    Console.WriteLine("🌍 " + tr.GetString());
            }
            catch (Exception err)
            {
                Console.WriteLine("❌ JSON parse error: " + err.Message);
            }
        };
        try
        {
            ws.Connect();
            if (!ws.IsAlive)
            {
                Console.WriteLine("❌ Failed to connect to WebSocket server. Exiting...");
                Console.WriteLine("❓ Make sure the server is running...");

                return;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("❌ WebSocket connection error: " + ex.Message);
            return;
        }
        Console.WriteLine("✅ Connected");

        // Initalize opus encoder
        var encoder = OpusCodecFactory.CreateEncoder(SampleRate, Channels, OpusApplication.OPUS_APPLICATION_VOIP);
        encoder.Bitrate = 30000; // Set bitrate to 30 kbps

        PortAudio.Initialize();

        var device = PortAudio.DefaultInputDevice;
        var info = PortAudio.GetDeviceInfo(device);

        var inputParams = new StreamParameters
        {
            device = device,
            channelCount = Channels,
            sampleFormat = SampleFormat.Int16,
            suggestedLatency = info.defaultLowInputLatency,
            hostApiSpecificStreamInfo = IntPtr.Zero
        };

        PortAudioSharp.Stream.Callback callback = (IntPtr input, IntPtr output, uint frameCount, ref StreamCallbackTimeInfo timeInfo, StreamCallbackFlags statusFlags, IntPtr userData) =>
        {
            short[] samples = new short[frameCount];
            Marshal.Copy(input, samples, 0, (int)frameCount);

            byte[] chunk = new byte[samples.Length * 2];
            Buffer.BlockCopy(samples, 0, chunk, 0, chunk.Length);

            Buffer.BlockCopy(chunk, 0, buffer, filled, chunk.Length);
            filled += chunk.Length;

            while (filled >= ChunkBytes)
            {
                byte[] toSend = new byte[ChunkBytes];
                Buffer.BlockCopy(buffer, 0, toSend, 0, ChunkBytes);

                // Convert to short array for Opus encoding
                short[] pcm = new short[ChunkSamples];
                Buffer.BlockCopy(toSend, 0, pcm, 0, ChunkBytes);

                // Encode to Opus
                // Max size for Opus packet. 640 bytes is very conservative for encoding 640 samples (1280 bytes) at 16kHz
                // not all 640 will be sent later. Slicing will be used based on encoder.Encode return value.
                byte[] encoded = new byte[640];
                int len = encoder.Encode(pcm.AsSpan(), ChunkSamples, encoded.AsSpan(), encoded.Length);

                if (ws != null && ws.IsAlive && len > 0)
                {
                    ws.Send(encoded[..len]); // Slice the array to the actual length
                    // or: ws.Send(encoded.Take(len).ToArray());
                }

                filled -= ChunkBytes;
                Buffer.BlockCopy(buffer, ChunkBytes, buffer, 0, filled);
            }

            return StreamCallbackResult.Continue;
        };

        var stream = new PortAudioSharp.Stream(
            inParams: inputParams,
            outParams: null,
            sampleRate: SampleRate,
            framesPerBuffer: ChunkSamples,
            streamFlags: StreamFlags.ClipOff,
            callback: callback,
            userData: IntPtr.Zero
        );

        Console.WriteLine("🎤 Streaming mic audio... Press Ctrl+C to stop.");
        stream.Start();

        Console.CancelKeyPress += (_, __) =>
        {
            Console.WriteLine("\n🛑 Exiting...");
            stream.Stop();
            stream.Dispose();
            PortAudio.Terminate();
            ws?.Close();
            Environment.Exit(0);
        };

        while (true)
        {
            Thread.Sleep(200);
        }
    }
}
