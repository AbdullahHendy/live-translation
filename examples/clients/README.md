# Client Examples

Minimal example clients in different environments (e.g. Node.js, C#, JavaScript, Go, Kotlin/Android) that demonstrate how to communicate with the live-translation server over **WebSocket** using the expected audio protocol:
**raw PCM, 16-bit, mono, 16kHz, 512-sample chunks i.e. 1024-byte chunks**.
Each clients shows how to parse the server's **JSON responses**.

---

## Examples List

* [Node.js](./nodejs/) – node.js client using `node-record-lpcm16` and `ws`
* [Browser (Javascript)](./browser_js/) – javascript client using `Web Audio API + AudioWorklet`
* [Go](./go_client/) – Go client using `malgo` (miniaudio) and `gorilla/websocket`
* [C#](./csharpclient/) – C# client using `PortAudioSharp2` and `WebSocketSharp`
* [Kotlin/Android](./android/) – Android client using `AudioRecord` and `OkHttp WebSocket`