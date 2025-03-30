import cv2
import threading
import asyncio
import websockets
import json

# Shared variable for translated text
text_to_display = "Waiting for translation..."
lock = threading.Lock()

def wrap_text(text, max_width, font, font_scale, thickness):

    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        (text_width, _), _ = cv2.getTextSize(test_line, font, font_scale, thickness)
        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    return lines

def start_websocket_listener():
    async def listen():
        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            print("🔌 Connected to Live Translation WebSocket server.")

            try:
                while True:
                    message = await websocket.recv()
                    print(f"Received message: {message}")
                    data = json.loads(message)
                    new_text = data.get("translation", "") # transcription or translation

                    with lock:
                        global text_to_display
                        text_to_display = new_text

            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed.")

    asyncio.run(listen())

# Launch WebSocket listener in a separate thread
ws_thread = threading.Thread(target=start_websocket_listener)
ws_thread.daemon = True
ws_thread.start()

# Face tracking with OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)


font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
thickness = 1

while True:
    # Read frame from the camera
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    with lock:
        current_text = text_to_display

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Draw the text box next to the face
        box_x = x + w + 10
        box_y = y
        box_width = 250
        box_height = h

        # Wrapped text lines
        lines = wrap_text(current_text, box_width - 10, font, font_scale, thickness)

        # Adjust height if needed
        line_height = 20
        text_box_height = line_height * len(lines) + 10
        text_box_width = box_width

        # Draw filled rectangle for better visibility
        cv2.rectangle(frame, (box_x, box_y), (box_x + text_box_width, box_y + text_box_height), (0, 255, 0), -1)

        # Draw each line
        for i, line in enumerate(lines):
            y_offset = box_y + 20 + i * line_height
            cv2.putText(frame, line, (box_x + 5, y_offset), font, font_scale, (0, 0, 0), thickness)

    cv2.imshow('Face Tracking with Live Translation', frame)

    if cv2.waitKey(1) == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()

