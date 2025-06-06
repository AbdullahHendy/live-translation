# Client Examples

Minimal example clients in different environments (e.g. Node.js, C#, JavaScript, Go, Kotlin/Android) that demonstrate how to communicate with the live-translation server over **WebSocket** using the **expected audio protocol**:
**Opus-decoded** raw PCM, 16-bit, mono, 16kHz, 640-sample chunks i.e. 1280-byte chunks.
> **NOTE**: The example clients can be easily modified to remove the opus encoding code and just send the **raw PCM** in case the server is run with the ***--codec pcm*** option.
>
**Each client** shows how to parse the server's **JSON responses**.

---

## Examples List

* [Node.js](./nodejs/) – node.js client using `node-record-lpcm16` and `ws`
* [Browser (Javascript)](./browser_js/) – javascript client using `Web Audio API + AudioWorklet`
* [Go](./go_client/) – Go client using `malgo` (miniaudio) and `gorilla/websocket`
* [C#](./csharpclient/) – C# client using `PortAudioSharp2` and `WebSocketSharp`
* [Kotlin/Android](./android/) – Android client using `AudioRecord` and `OkHttp WebSocket`