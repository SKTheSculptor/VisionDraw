VisionDraw

A touchless drawing application using hand gesture recognition with OpenCV and MediaPipe.

Features

Hand Gesture Drawing: Draw on a virtual canvas using index finger gestures

Real-time Camera Feed: Live video feed displayed in the top-right corner

Selective Erase: Select and erase specific drawn regions with two-finger gesture

Full Canvas Clear: Clear entire canvas using a keyboard shortcut

Intuitive Layout: Split-screen design with drawing canvas on the left and controls on the right

Requirements

Python 3.7+

OpenCV

MediaPipe

NumPy

Installation

Clone the repository:

git clone https://github.com/SKTheSculptor/VisionDraw.git
cd VisionDraw


Install dependencies:

pip install opencv-python mediapipe numpy

Usage

Run the application:

python main.py

Controls
Gestures

Index Finger Up: Draw mode – move finger to draw on canvas

Index + Middle Finger Up: Selection mode – select region to erase

Keyboard

Q: Quit application

E: Select drawn region for deletion

ENTER: Confirm deletion of selected region

ESC: Cancel selection

C: Clear entire canvas

How It Works

The application uses MediaPipe's hand tracking to detect finger positions and gestures.
The screen is divided into:

Left Area (75%): Drawing canvas where users draw using hand gestures

Top-Right Area (25%): Live camera feed showing hand movements

Bottom-Right Area: Instruction panel with control details

Coordinates are automatically scaled to ensure accurate drawing across the canvas area
