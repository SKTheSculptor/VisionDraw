import cv2
import numpy as np
import time
import handTrackerMod as htm

# -------------------- Basic Settings --------------------
brushThickness = 5          # Thickness of drawing brush
eraserThickness = 30        # Thickness of eraser
drawColor = (0, 0, 255)     # Default drawing color (Red)

DRAW_TIMEOUT = 0.35         # Time gap to start a new stroke
MAX_JUMP = 80               # Max allowed finger jump to continue a stroke
SCALE_X = 800 / 1280        # Scale factor for mapping camera to canvas

# -------------------- Camera Setup --------------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 1280)
cap.set(4, 720)

# Hand detector initialization
detector = htm.handDetector(detectionConf=0.85)

# Variables to track drawing state
xprev, yprev = 0, 0
is_drawing = False
last_draw_time = 0.0

# -------------------- Canvas & Display --------------------
CANVAS_H, CANVAS_W = 720, 800
imgCanvas = np.zeros((CANVAS_H, CANVAS_W, 3), np.uint8)

DISPLAY_H, DISPLAY_W = 720, 1280
imgDisplay = np.zeros((DISPLAY_H, DISPLAY_W, 3), np.uint8)

# Check camera availability
if not cap.isOpened():
    print("Could not open video device")
    exit(0)

# -------------------- Helper Functions --------------------
# Find bounding box of drawn content on canvas
def bbox_of_canvas(canvas):
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    x_min = min(cv2.boundingRect(c)[0] for c in contours)
    y_min = min(cv2.boundingRect(c)[1] for c in contours)
    x_max = max(cv2.boundingRect(c)[0] + cv2.boundingRect(c)[2] for c in contours)
    y_max = max(cv2.boundingRect(c)[1] + cv2.boundingRect(c)[3] for c in contours)

    pad = 6
    return (
        max(0, x_min - pad),
        max(0, y_min - pad),
        min(canvas.shape[1] - 1, x_max + pad),
        min(canvas.shape[0] - 1, y_max + pad)
    )

# Clear a selected region on canvas
def clear_region(canvas, bbox):
    if bbox:
        x1, y1, x2, y2 = bbox
        canvas[y1:y2 + 1, x1:x2 + 1] = 0

# Calculate distance between two points
def dist(a, b):
    return int(((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5)

# -------------------- Selection Variables --------------------
selection_pending = None
selection_shown_at = None
SELECTION_TIMEOUT = 8.0

print("Controls: q=quit | e=select | ENTER=delete | ESC=cancel | c=clear")

# -------------------- Main Loop --------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip camera for mirror effect
    frame = cv2.flip(frame, 1)

    # Detect hand and landmarks
    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame, draw=False)
    now = time.time()

    if lmList:
        # Index and middle finger positions
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        fingers = detector.fingersUp()

        # Selection mode (index + middle finger)
        if fingers[1] and fingers[2]:
            is_drawing = False
            xprev, yprev = 0, 0
            cv2.rectangle(frame, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

        # Drawing mode (only index finger)
        elif fingers[1] and not fingers[2]:
            cv2.circle(frame, (x1, y1), 10, drawColor, cv2.FILLED)

            # Scale x-coordinate for canvas
            x1s, y1s = int(x1 * SCALE_X), y1
            xps, yps = int(xprev * SCALE_X) if xprev else 0, yprev

            # Decide whether to start a new stroke
            start_new = (
                not is_drawing or
                (now - last_draw_time) > DRAW_TIMEOUT or
                (xprev and dist((xprev, yprev), (x1, y1)) > MAX_JUMP)
            )

            # Draw line if continuing stroke
            if not start_new:
                thickness = eraserThickness if drawColor == (0, 0, 0) else brushThickness
                cv2.line(imgCanvas, (xps, yps), (x1s, y1s), drawColor, thickness)

            xprev, yprev = x1, y1
            is_drawing = True
            last_draw_time = now

        # No drawing gesture
        else:
            is_drawing = False
            xprev, yprev = 0, 0
    else:
        is_drawing = False
        xprev, yprev = 0, 0

    # -------------------- Display Composition --------------------
    imgDisplay[:] = 0

    # Camera preview (top-right)
    frame_resized = cv2.resize(frame, (480, 270))
    imgDisplay[0:270, 800:1280] = frame_resized

    # Canvas area (left)
    imgDisplay[0:720, 0:800] = imgCanvas

    # Highlight selected area
    if selection_pending:
        x1s, y1s, x2s, y2s = selection_pending
        overlay = imgDisplay[0:720, 0:800].copy()
        cv2.rectangle(overlay, (x1s, y1s), (x2s, y2s), (0, 255, 255), -1)
        imgDisplay[0:720, 0:800] = cv2.addWeighted(overlay, 0.33, imgDisplay[0:720, 0:800], 0.67, 0)
        cv2.rectangle(imgDisplay, (x1s, y1s), (x2s, y2s), (0, 255, 255), 2)

        # Auto-cancel selection after timeout
        if selection_shown_at and time.time() - selection_shown_at > SELECTION_TIMEOUT:
            selection_pending = None
            selection_shown_at = None

    cv2.imshow("VisionDraw", imgDisplay)
    key = cv2.waitKey(1) & 0xFF

    # -------------------- Keyboard Controls --------------------
    if key == ord('q'):
        break
    if key == ord('e'):
        selection_pending = bbox_of_canvas(imgCanvas)
        selection_shown_at = time.time()
    if key == 13 and selection_pending:
        clear_region(imgCanvas, selection_pending)
        selection_pending = None
    if key == 27:
        selection_pending = None
    if key == ord('c'):
        imgCanvas[:] = 0

cap.release()
cv2.destroyAllWindows()
