# VisionDraw

**VisionDraw** is a touchless drawing application that allows users to draw on a digital canvas using hand gesture recognition with OpenCV and MediaPipe.

# Features
- **Hand Gesture Drawing**: Draw on a virtual canvas using index finger gestures
- **Real-time Camera Feed**: Live webcam feed displayed in the top-right corner
- **Selective Erase**: Select and erase specific drawn regions using a two-finger gesture
- **Full Canvas Clear**: Clear the entire canvas using a keyboard shortcut
- **Intuitive Layout**: Split-screen design with the drawing canvas on the left and controls on the right

# Requirements
- **Python 3.7+**
- **OpenCV**
- **MediaPipe**
- **NumPy**

# Installation
Clone the Repository:
git clone https://github.com/SKTheSculptor/VisionDraw.git
cd VisionDraw

Install Dependencies:
pip install opencv-python mediapipe numpy

# Usage
python main.py

# Controls

Hand Gestures:
- **Index Finger Up**: Draw Mode – move finger to draw on the canvas
- **Index + Middle Finger Up**: Selection Mode – select region to erase

Keyboard:
- **Q**     : Quit application
- **E**     : Select drawn region for deletion
- **ENTER** : Confirm deletion of selected region
- **ESC**   : Cancel selection
- **C**     : Clear entire canvas

# How It Works
- Uses **MediaPipe hand tracking** to detect finger positions and gestures
- **OpenCV** maps finger movement to the drawing canvas
- Gesture logic controls drawing, selection, and erasing

# Screen Layout
- **Left Area (75%)**: Drawing canvas controlled using hand gestures
- **Top-Right Area (25%)**: Live camera feed showing hand movement
- **Bottom-Right Area**: Instruction panel with controls

Note:
Coordinates are automatically scaled to ensure accurate drawing across the canvas area.
