# Virtual Painter

A touchless drawing application using hand gesture recognition with OpenCV and MediaPipe.

## Features

- **Hand Gesture Drawing**: Draw on a virtual canvas using index finger gestures
- **Real-time Camera Feed**: Live video feed displayed in the top-right corner
- **Selective Erase**: Select and erase specific drawn regions with two-finger gesture
- **Full Canvas Clear**: Clear entire canvas with keyboard shortcut
- **Intuitive Layout**: Split-screen design with drawing canvas on the left and controls on the right

## Requirements

- Python 3.7+
- OpenCV
- MediaPipe
- NumPy

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/virtual-painter.git
   cd virtual-painter
   ```

2. Install dependencies:
   ```bash
   pip install opencv-python mediapipe numpy
   ```

## Usage

Run the application:
```bash
python main.py
```

## Controls

### Gestures:
- **Index Finger Up**: Draw mode - move finger to draw on canvas
- **Index + Middle Finger Up**: Selection mode - select region to erase

### Keyboard:
- **Q**: Quit application
- **E**: Select drawn region for deletion
- **ENTER**: Confirm deletion of selected region
- **ESC**: Cancel selection
- **C**: Clear entire canvas

## How It Works

The application uses MediaPipe's hand tracking to detect finger positions and gestures. The screen is divided into:
- **Left Area (75%)**: Drawing canvas where you can draw with hand gestures
- **Top-Right Area (25%)**: Live camera feed showing your hand
- **Bottom-Right Area**: Instruction panel with controls

Coordinates are automatically scaled to ensure accurate drawing across the canvas area.

