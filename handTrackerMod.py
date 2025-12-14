# handTrackerMod.py
import cv2 
import mediapipe as mp
import time

class handDetector():
  def __init__(self, mode=False, maxHands=3, complexity=1, detectionConf=0.5, trackCon=0.5):
    self.mode = mode
    self.maxhands = maxHands
    self.complexity = complexity
    self.detectionConf = detectionConf
    self.trackCon = trackCon

    self.mpHands = mp.solutions.hands
    # Keep parameter order same as MediaPipe expects (we pass ours in same order)
    self.hands = self.mpHands.Hands(self.mode, self.maxhands, self.complexity, self.detectionConf, self.trackCon)
    self.mpDraw = mp.solutions.drawing_utils

    self.tipIds = [4, 8, 12, 16, 20]
    self.results = None
    self.lmList = []

  def findHands(self, frame, draw=True):
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    self.results = self.hands.process(imgRGB)

    if self.results.multi_hand_landmarks:
        for handLms in self.results.multi_hand_landmarks:
            if draw:
              self.mpDraw.draw_landmarks(frame, handLms, self.mpHands.HAND_CONNECTIONS)

    return frame
  

  def findPosition(self, frame, handNo=0, draw=True):
    """
    returns list of [id, cx, cy] in pixel coords for specified handNo
    """
    self.lmList = []
    if self.results and self.results.multi_hand_landmarks:  
      myHand = self.results.multi_hand_landmarks[handNo]

      for id, lm, in enumerate(myHand.landmark):
          h, w, c = frame.shape
          cx, cy = int(lm.x * w), int(lm.y * h)
          self.lmList.append([id, cx, cy])
          if draw:
            cv2.circle(frame, (cx, cy), 5, (255, 255, 255), cv2.FILLED)

    return self.lmList
  

  def fingersUp(self):
    """
    returns list: [thumb, index, middle, ring, pinky] with 1 if finger up else 0
    Requires findPosition() to be called previously so self.lmList is populated.
    """
    fingers = []

    if not self.lmList:
      return [0,0,0,0,0]

    # thumb (x compare)
    try:
      if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0] - 1][1]:
        fingers.append(1)
      else:
        fingers.append(0)
    except:
      fingers.append(0)

    # 4 fingers (y compare)
    for id in range(1, 5):
      try:
        if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
          fingers.append(1)
        else:
          fingers.append(0)
      except:
        fingers.append(0)
    
    return fingers

  def get_normalized_tip(self, frame, handNo=0):
    """
    Returns (nx, ny) for index fingertip relative to frame (0..1). 
    If no hand detected returns None.
    This is a convenience so callers can map to any coordinate system easily.
    """
    if not (self.results and self.results.multi_hand_landmarks):
      return None
    try:
      myHand = self.results.multi_hand_landmarks[handNo]
      # landmark 8 is index tip
      lm = myHand.landmark[8]
      # lm.x and lm.y are normalized relative to the passed frame
      return (lm.x, lm.y)
    except Exception:
      return None

# The rest of your test `main()` can remain unchanged if you want to keep it for debugging.
if __name__ == "__main__":
  # optional quick debug runner
  from time import time
  cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
  detector = handDetector()
  if not cap.isOpened():
    print("Could not open camera")
    exit()
  while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame)
    if lmList:
      print("Index tip pixel:", lmList[8])
      norm = detector.get_normalized_tip(frame)
      if norm:
        print("Index tip normalized:", norm)
    cv2.imshow("Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  cap.release()
  cv2.destroyAllWindows()
