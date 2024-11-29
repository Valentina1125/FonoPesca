# FacialTherapyGame

A gamified facial therapy system using computer vision that helps patients with central facial paralysis perform rehabilitation exercises through interactive gaming mechanics. The facial metrics module is a modified version of [Emotrics](https://github.com/dguari1/Emotrics).

## Description

FacialTherapyGame is a thesis project that integrates computer vision and gaming to create an engaging rehabilitation tool for facial therapy. The system:

- Uses real-time facial gesture recognition to detect and classify therapeutic facial movements
- Integrates a modified version of Emotrics for facial symmetry analysis and metric calculation
- Transforms traditional facial exercises into interactive gameplay through a fishing-themed game
- Provides quantitative metrics and feedback based on Emotrics' facial measurement algorithms
- Aims to improve therapy adherence by making exercises more engaging and motivating

## Features

- Real-time facial gesture detection and classification using CNN
- Facial metrics analysis powered by modified Emotrics algorithms:
  - Facial symmetry measurements
  - Range of motion tracking
  - Landmark detection and analysis
- Interactive fishing game controlled by facial movements
- Progress tracking and performance metrics
- Adjustable difficulty levels
- Visualization of facial metrics and session data
- Support for three key therapeutic gestures: kiss, smile, and mouth opening

## System Requirements

- Python 3.10.11
- Windows OS (tested on Windows 11)
- Webcam

## Installation

1. Clone the repository:
```bash
git clone [repository URL]
cd FacialTherapyGame
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Main Dependencies

- OpenCV (4.10.0.84) - Video capture and image processing
- dlib (19.22.99) - Facial landmark detection 
- PyTorch (2.2.2) - Deep learning framework
- TensorFlow Intel (2.17.0) - Neural network optimization
- PyQt5 (5.15.11) - GUI framework
- pygame (2.6.1) - Game engine

## Usage

1. Activate the virtual environment
2. Run the main application:
```bash
python main.py
```



## License

© 2024 Valentina Uribe Salcedo. All rights reserved.
Universidad de los Andes, Colombia.
