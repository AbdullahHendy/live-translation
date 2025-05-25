/**
 * Live Translation C# Client (PortAudioSharp2 + WebSocketSharp)
 *
 * This program captures raw PCM audio from the system microphone and streams it
 * to a WebSocket server for real-time transcription and translation.
 *
 * Server-side expectations:
 * - Format:       Raw PCM
 * - Sample Rate:  16,000 Hz
 * - Channels:     Mono (1 channel)
 * - Bit Depth:    16-bit (signed int16) → 2 bytes per sample
 * - Chunk Size:   512 samples of 16-bit mono audio (1024 bytes)
 *
 * Audio is buffered and transmitted in fixed-size 512-sample chunks, matching exactly what the server expects.
 * Uses PortAudioSharp2 for cross-platform microphone input, and WebSocketSharp for client-server communication.
 */

using System.Runtime.InteropServices;
using PortAudioSharp;
using WebSocketSharp;

class Program
{
    const int SampleRate = 16000;
    const int Channels = 1;
    const int ChunkSamples = 512;
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
        ws.Connect();
        Console.WriteLine("✅ Connected");

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
                ws.Send(toSend);

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
