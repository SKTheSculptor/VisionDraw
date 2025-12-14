# VISIONDRAW

VisionDraw is a touchless drawing application that allows users to draw on a digital canvas using hand gesture recognition using OpenCV and MediaPipe.


# FEATURES

- Hand Gesture Drawing:
  Draw on a virtual canvas using index finger gestures.

- Real-time Camera Feed:
  Live webcam feed displayed in the top-right corner.

- Selective Erase:
  Select and erase specific drawn regions using a two-finger gesture.

- Full Canvas Clear:
  Clear the entire canvas using a keyboard shortcut.

- Intuitive Layout:
  Split-screen design with the drawing canvas on the left and controls on the right.


# REQUIREMENTS

- Python 3.7 or above
- OpenCV
- MediaPipe
- NumPy


# INSTALLATION

## Clone the Repository
git clone https://github.com/SKTheSculptor/VisionDraw.git
cd VisionDraw

## Install Dependencies
pip install opencv-python mediapipe numpy


# USAGE

Run the application using:
python main.py


# CONTROLS

## Hand Gestures

- Index Finger Up:
  Draw Mode – move finger to draw on the canvas.

- Index + Middle Finger Up:
  Selection Mode – select a region to erase.


## Keyboard Controls

- Q     : Quit the application
- E     : Select drawn region for deletion
- ENTER : Confirm deletion of selected region
- ESC   : Cancel selection
- C     : Clear the entire canvas


# HOW IT WORKS

- The application uses MediaPipe hand tracking to detect finger positions and gestures.
- OpenCV processes the video feed and maps finger movements to the drawing canvas.
- Gesture-based logic determines whether the user is drawing, selecting, or erasing.


# SCREEN LAYOUT

- Left Area (75%):
  Drawing canvas controlled using hand gestures.

- Top-Right Area (25%):
  Live camera feed showing hand movement.

- Bottom-Right Area:
  Instruction panel with controls.

Note:
Coordinates are automatically scaled to ensure accurate drawing across the canvas area.
