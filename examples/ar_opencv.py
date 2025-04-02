import cv2
import asyncio
import websockets
import json
import subprocess
import threading
import time
import argparse
import signal
import sys

# Config
WS_PORT = 8765
BOX_WIDTH = 300
LINE_HEIGHT = 25
MAX_LINES = 10
MARGIN = 20
FONT = cv2.FONT_HERSHEY_COMPLEX
FONT_SCALE = 0.7
THICKNESS = 2
TEXT_TIMEOUT = 4

# Shared translation text
latest_translation = {"text": "", "timestamp": time.time()}
exit_event = threading.Event()


def decide_side(x, w, frame_width):
    space_left = x
    space_right = frame_width - (x + w)
    return "right" if space_right >= space_left else "left"


def wrap_text(text, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        text_size, _ = cv2.getTextSize(test_line, FONT, FONT_SCALE, THICKNESS)
        if text_size[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines[:MAX_LINES]


async def websocket_listener(shared_text, transcription_only=False):
    uri = f"ws://localhost:{WS_PORT}"
    while not exit_event.is_set():
        try:
            async with websockets.connect(uri) as websocket:
                print("🌐 Connected to WebSocket server")
                while not exit_event.is_set():
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    key = "transcription" if transcription_only else "translation"
                    translation = data.get(key, "")
                    shared_text["text"] = translation
                    shared_text["timestamp"] = time.time()
        except Exception as e:
            if exit_event.is_set():
                break
            print(f"🔁 WebSocket reconnecting: {e}")
            await asyncio.sleep(2)


def start_ws_listener(shared_text, transcription_only=False):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_listener(shared_text, transcription_only))


def start_server_proc(transcription_only=False):
    args = [
        sys.executable,
        "-m",
        "live_translation.cli",
        "--output",
        "websocket",
        "--ws_port",
        str(WS_PORT),
    ]
    if transcription_only:
        args.append("--transcribe_only")

    return subprocess.Popen(args)


def shutdown(proc):
    if proc and proc.poll() is None:
        # Send SIGINT instead of terminate to act like Ctrl+C
        proc.send_signal(signal.SIGINT)
        proc.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--transcription_only",
        action="store_true",
        help="Overlay only the transcription text",
    )
    args = parser.parse_args()

    # Start the server process
    server_proc = start_server_proc(args.transcription_only)

    # Start the websocket listener
    ws_thread = threading.Thread(
        target=start_ws_listener, args=(latest_translation, args.transcription_only)
    )
    ws_thread.start()

    # Start webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        shutdown(server_proc)
        return

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cv2.namedWindow("Live Translation Face Overlay", cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Clear old text
            if time.time() - latest_translation["timestamp"] > TEXT_TIMEOUT:
                latest_translation["text"] = ""

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)
            face = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)

            if face:
                x, y, w, h = face[0]
                frame_width = frame.shape[1]
                side = decide_side(x, w, frame_width)

                if side == "right":
                    box_x = min(x + w + MARGIN, frame_width - BOX_WIDTH)
                else:
                    box_x = max(x - BOX_WIDTH - MARGIN, 0)

                box_y = max(y, LINE_HEIGHT)

                lines = wrap_text(latest_translation["text"], BOX_WIDTH)
                for i, line in enumerate(lines):
                    text_pos = (box_x, box_y + i * LINE_HEIGHT)
                    cv2.putText(
                        frame,
                        line,
                        text_pos,
                        FONT,
                        FONT_SCALE,
                        (255, 255, 255),
                        THICKNESS,
                    )

            cv2.imshow("Live Translation Face Overlay", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        pass

    finally:
        exit_event.set()
        ws_thread.join(timeout=2)
        shutdown(server_proc)
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
