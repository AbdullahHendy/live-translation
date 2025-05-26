// worklet-processor.js
class PCMProcessor extends AudioWorkletProcessor {
    process(inputs) {
        const input = inputs[0];
        if (input.length > 0) {
            const channelData = input[0]; // mono
            this.port.postMessage(channelData.slice()); // send to main thread
        }
        return true;
    }
}

registerProcessor('pcm-processor', PCMProcessor);
