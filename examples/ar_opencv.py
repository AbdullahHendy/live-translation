import argparse
import time
from PIL import ImageFont, ImageDraw, Image
import cv2
import asyncio
import threading
import numpy as np

WS_PORT = 8765

BOX_WIDTH = 300
LINE_HEIGHT = 25
MAX_LINES = 10
MARGIN = 20
FONT = cv2.FONT_HERSHEY_COMPLEX
FONT_SCALE = 0.6
THICKNESS = 2

TEXT_TIMEOUT = 4

latest_text = {"text": "", "timestamp": time.time()}


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


def get_font_path(tgt_lang):
    """
    NOTE:
    The font path may need to be adjusted based on your system if not installed in the
    default path for PIL: /usr/share/fonts/*
    Ubuntu 24.10
    """

    font_map = {
        "ar": "NotoSansArabic-Bold.ttf",  # Arabic
        "ur": "NotoSansArabic-Bold.ttf",  # Urdu
        "hi": "NotoSansDevanagari-Bold.ttf",  # Hindi
        "th": "NotoSansThai-Bold.ttf",  # Thai
        "zh": "NotoSansCJK-Bold.ttc",  # Chinese
        "ja": "NotoSansCJK-Bold.ttc",  # Japanese
        "ko": "NotoSansCJK-Bold.ttc",  # Korean
    }

    # Default fallback to NotoSans-Bold.ttf if the target language is not in the map
    return font_map.get(tgt_lang, "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf")


def draw_unicode_text(
    frame,
    text,
    position,
    font_path="NotoSans-Bold.ttf",
    font_size=20,
    color=(255, 255, 255),
    debug=False,
):
    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"❌ Could not load font: {e}")
        font = ImageFont.load_default()

    if debug:
        # Measure text and draw background
        text_size = draw.textbbox(position, text, font=font)
        draw.rectangle(text_size, fill=(100, 100, 100))  # dark gray bg

    draw.text(position, text, font=font, fill=color)
    return np.array(img_pil)


def run_camera(tgt_lang, debug=False):
    print("📸 Opening webcam...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open webcam.")
        return
    print("✅ Webcam opened. Press 'q' to quit.")

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cv2.namedWindow("Live Translation Face Overlay", cv2.WINDOW_NORMAL)

    font_path = get_font_path(tgt_lang)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Clear old text after TEXT_TIMEOUT seconds
        if time.time() - latest_text["timestamp"] > TEXT_TIMEOUT:
            latest_text["text"] = ""

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        # Sort faces by area (width * height)
        face = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)

        if face:
            # Get the largest face
            x, y, w, h = face[0]
            # Draw a rectangle around the face
            if debug:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)
            frame_width = frame.shape[1]
            side = decide_side(x, w, frame_width)

            if side == "right":
                box_x = min(x + w + MARGIN, frame_width - BOX_WIDTH)
            else:
                box_x = max(x - BOX_WIDTH - MARGIN, 0)

            box_y = max(y, LINE_HEIGHT)

            lines = wrap_text(latest_text["text"], BOX_WIDTH)

            # NOTE:
            # Font size based on face height
            # This is empirical based on one case and it follows linear interpolation
            # with NEGATIVE slope:
            # max_font   +   (max_font - min_font) / (min_h - max_h)   *   (h - min_h)
            # min and max height are based on the face height (variable h)
            # min and max font size are based on choice
            font_size = int(max(18, min(22, 22 + (22 - 18) / (120 - 320) * (h - 120))))

            for i, line in enumerate(lines):
                text_pos = (box_x, box_y + i * LINE_HEIGHT)

                # NOTE:
                # Using a custom drawing function to support Unicode characters instead
                # of OpenCV's built-in text cv2.putText() frunction.
                frame = draw_unicode_text(
                    frame,
                    line,
                    text_pos,
                    font_path=font_path,
                    font_size=font_size,
                    debug=debug,
                )

        cv2.imshow("Live Translation Face Overlay", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


async def start_live_translation(
    src_lang, tgt_lang, device, whisper_model, transcription_only
):
    # NOTE:
    # live_translation components are imported inside the function instead of at the
    # top-level because these modules spawn multiprocessing contexts at import time.
    # That interferes with OpenCV's ability to open the GUI window
    # (tested on GTK/X11 on Linux).
    # Delaying the import allows for a self-contained start_live_translation() so it can
    # be called later in its own context outside of OpenCVs'.
    from live_translation import LiveTranslationServer, ServerConfig
    from live_translation import LiveTranslationClient, ClientConfig

    server = LiveTranslationServer(
        ServerConfig(
            ws_port=WS_PORT,
            transcribe_only=transcription_only,
            device=device,
            whisper_model=whisper_model,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
        )
    )
    pipeline = server.run(blocking=False)

    def callback(entry):
        key = "transcription" if transcription_only else "translation"
        text = entry.get(key, "")

        latest_text["text"] = text
        latest_text["timestamp"] = time.time()
        print("📝", text) if transcription_only else print("🌍", text)
        return False

    client = LiveTranslationClient(ClientConfig(server_uri=f"ws://localhost:{WS_PORT}"))
    try:
        await client.run(callback=callback, blocking=False)
    finally:
        client.stop()
        pipeline.stop()


def run_live_translation_thread(
    src_lang, tgt_lang, device, whisper_model, transcription_only
):
    asyncio.run(
        start_live_translation(
            src_lang, tgt_lang, device, whisper_model, transcription_only
        )
    )


if __name__ == "__main__":
    # 1. Parse command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("--src_lang", type=str, default="en")
    parser.add_argument("--tgt_lang", type=str, default="es")
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--whisper_model", type=str, default="base")
    parser.add_argument("--transcription_only", action="store_true")

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug to show face box and add background to text.",
    )
    args = parser.parse_args()

    # 2. Start live translation stack in a separate thread
    # NOTE:
    # Background thread is used to run the async live_translation stack.
    # `asyncio.run(start_live_translation())` is NOT called directly because:
    #   - It would prevent OpenCV's GUI from starting due to live_translation stack
    #       starting multiprocessing components that interferes with OpenCV's
    #       GTK/X11 GUI rendering.
    # Instead, manually create a new event loop in a separate thread, then run the
    # live_translation stack there without interfering with OpenCV in the main thread.
    #
    # This setup has been tested on Ubuntu 24.10 with X11. Behavior may differ under
    # Wayland, or other operating systems in general due to GUI backend differences.
    thread = threading.Thread(
        target=run_live_translation_thread,
        args=(
            args.src_lang,
            args.tgt_lang,
            args.device,
            args.whisper_model,
            args.transcription_only,
        ),
    )
    thread.start()

    # 3. Start webcam and overlay text
    run_camera(args.tgt_lang, debug=args.debug)
    print("\n📸 Closing webcam. Press CTRL+C to exit!\n")

    # When camera loop ends (using 'q'), wait for the live_translation thread to finish.
    while thread.is_alive():
        try:
            thread.join(timeout=1)
        except KeyboardInterrupt:
            pass
