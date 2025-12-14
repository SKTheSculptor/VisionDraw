import cv2
import numpy as np
import time
import handTrackerMod as htm

# ---------- settings ----------
brushThickness = 5      # thin pen
eraserThickness = 30    # eraser thickness
drawColor = (0, 0, 255)  # default RED

# thresholds to avoid unwanted connecting lines
DRAW_TIMEOUT = 0.35   # seconds: if pause > this, start a new stroke
MAX_JUMP = 80         # pixels: if distance > this, don't connect (start new stroke)

# scaling for canvas (800x720 from 1280x720)
SCALE_X = 800 / 1280

# camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector(detectionConf=0.85)
xprev, yprev = 0, 0
is_drawing = False
last_draw_time = 0.0

# canvas (left area: 800x720)
CANVAS_H = 720
CANVAS_W = 800
imgCanvas = np.zeros((CANVAS_H, CANVAS_W, 3), np.uint8)

# display (composite image: 1280x720)
DISPLAY_H = 720
DISPLAY_W = 1280
imgDisplay = np.zeros((DISPLAY_H, DISPLAY_W, 3), np.uint8)

if not (cap.isOpened()):
    print("Could not open video device")
    exit(0)

# ---------- helper functions ----------
def bbox_of_canvas(canvas):
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    x_min = min([cv2.boundingRect(c)[0] for c in contours])
    y_min = min([cv2.boundingRect(c)[1] for c in contours])
    x_max = max([cv2.boundingRect(c)[0] + cv2.boundingRect(c)[2] for c in contours])
    y_max = max([cv2.boundingRect(c)[1] + cv2.boundingRect(c)[3] for c in contours])

    pad = 6
    x1 = max(0, x_min - pad)
    y1 = max(0, y_min - pad)
    x2 = min(canvas.shape[1]-1, x_max + pad)
    y2 = min(canvas.shape[0]-1, y_max + pad)
    return (x1, y1, x2, y2)

def clear_region(canvas, bbox):
    if bbox is None:
        return
    x1, y1, x2, y2 = bbox
    canvas[y1:y2+1, x1:x2+1] = 0

def dist(a, b):
    return int(((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5)

# ---------- main loop ----------
selection_pending = None
selection_shown_at = None
SELECTION_TIMEOUT = 8.0

print("Controls: q=quit | e=select written region | ENTER=delete | ESC=cancel | c=clear all")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera read failed")
        break

    frame = cv2.flip(frame, 1)

    # detect hands
    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame, draw=False)

    now = time.time()

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]     # index finger tip
        x2, y2 = lmList[12][1:]    # middle finger tip

        fingers = detector.fingersUp()

        # Selection mode (two fingers up) - no drawing while selecting
        if fingers[1] and fingers[2]:
            # when in selection mode, treat as pen-up
            is_drawing = False
            xprev, yprev = 0, 0
            cv2.rectangle(frame, (x1, y1-25), (x2, y2+25), drawColor, cv2.FILLED)

        # Drawing mode - index finger only
        elif fingers[1] and not fingers[2]:
            cv2.circle(frame, (x1, y1), 10, drawColor, cv2.FILLED)

            # Scale coordinates for canvas
            x1_scaled = int(x1 * SCALE_X)
            y1_scaled = y1
            xprev_scaled = int(xprev * SCALE_X) if xprev != 0 else 0
            yprev_scaled = yprev

            # Should we start a new stroke instead of connecting?
            start_new_stroke = False

            if not is_drawing:
                # just entered drawing mode -> new stroke
                start_new_stroke = True
            else:
                # if time since last draw is long -> new stroke
                if (now - last_draw_time) > DRAW_TIMEOUT:
                    start_new_stroke = True
                else:
                    # if pointer jumped far -> new stroke
                    if xprev != 0 or yprev != 0:
                        jump = dist((xprev, yprev), (x1, y1))
                        if jump > MAX_JUMP:
                            start_new_stroke = True

            if start_new_stroke:
                # start a new stroke: set previous to current (no connecting line)
                xprev, yprev = x1, y1
            else:
                # continue stroke: draw line from previous to current on canvas only
                if drawColor == (0,0,0):  # eraser
                    cv2.line(imgCanvas, (xprev_scaled, yprev_scaled), (x1_scaled, y1_scaled), drawColor, eraserThickness)
                else:
                    cv2.line(imgCanvas, (xprev_scaled, yprev_scaled), (x1_scaled, y1_scaled), drawColor, brushThickness)

                xprev, yprev = x1, y1

            # mark drawing state and time of last point
            is_drawing = True
            last_draw_time = now

        else:
            # finger not in drawing pose -> treat as pen lifted
            is_drawing = False
            xprev, yprev = 0, 0

    else:
        # no landmarks detected -> pen lifted
        is_drawing = False
        xprev, yprev = 0, 0

    # Create composite display
    imgDisplay[:] = 0  # reset to black

    # Resize camera feed to 480x270 (preserve aspect ratio, fit height 480)
    frame_resized = cv2.resize(frame, (480, 270))

    # Place camera feed in top-right (y=0-270, x=800-1280)
    imgDisplay[0:270, 800:1280] = frame_resized

    # Instruction panel below camera (y=270-480, x=800-1280) - black background
    imgDisplay[270:480, 800:1280] = 0
    cv2.putText(imgDisplay, "Q -> Quit", (810, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    cv2.putText(imgDisplay, "E -> Clear", (810, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    # Place canvas in left area (y=0-720, x=0-800)
    imgDisplay[0:720, 0:800] = imgCanvas

    # Show selection if active on canvas area
    if selection_pending is not None:
        x1s, y1s, x2s, y2s = selection_pending
        overlay = imgDisplay[0:720, 0:800].copy()
        cv2.rectangle(overlay, (x1s, y1s), (x2s, y2s), (0,255,255), -1)
        alpha = 0.33
        imgDisplay[0:720, 0:800] = cv2.addWeighted(overlay, alpha, imgDisplay[0:720, 0:800], 1-alpha, 0)
        cv2.rectangle(imgDisplay, (x1s, y1s), (x2s, y2s), (0,255,255), 2)
        cv2.putText(imgDisplay, "ENTER=Delete | ESC=Cancel", (x1s, max(30, y1s-8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        if selection_shown_at and (time.time() - selection_shown_at > SELECTION_TIMEOUT):
            selection_pending = None
            selection_shown_at = None

    cv2.imshow("Virtual Painter", imgDisplay)
    key = cv2.waitKey(1) & 0xFF

    # Key controls
    if key == ord('q'):
        break

    if key == ord('e'):
        bb = bbox_of_canvas(imgCanvas)
        if bb is None:
            print("Nothing drawn to erase.")
        else:
            selection_pending = bb
            selection_shown_at = time.time()
            print("Selection active. Press ENTER to delete.")
        continue

    if key == 13 and selection_pending is not None:   # ENTER
        clear_region(imgCanvas, selection_pending)
        print("Selected area erased.")
        selection_pending = None
        selection_shown_at = None
        continue

    if key == 27:   # ESC
        selection_pending = None
        selection_shown_at = None
        print("Selection cancelled.")
        continue

    if key == ord('c'):
        imgCanvas[:] = 0
        print("Canvas cleared.")
        continue

# cleanup
cap.release()
cv2.destroyAllWindows()
