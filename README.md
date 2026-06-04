# Depression Detection Using Deep Learning with Chatbot Support

A full-stack web application that detects signs of depression through facial expression analysis and speech-to-text sentiment classification, built with Flask and powered by a CNN model and Naive Bayes classifier.

---

## Overview

Depression is one of the most underdiagnosed mental health conditions globally. Traditional diagnosis methods rely heavily on self-reporting and subjective clinical assessment. This system provides an objective, automated approach to early depression detection by analyzing two key signals — facial expressions from video input and spoken language patterns — using machine learning.

---

## Features

- **Facial Expression Analysis** — Real-time emotion detection using a Convolutional Neural Network trained on 7 emotion classes. Sustained detection of sadness or fear over 15 consecutive frames flags a depression indicator.
- **Speech-to-Text Mining** — Extracts audio from uploaded video, converts it to text using Google Speech Recognition, and classifies it using a Naive Bayes classifier trained on labeled depression-related text data.
- **User Authentication** — Secure registration and login with password recovery via security question.
- **History Dashboard** — Date-wise records of all video and text analysis results stored in a local SQLite database.
- **Chatbot Support** — Rule-based chatbot providing resources (videos, books, quotes) based on the user's stated concern area (financial, health, relationships).
- **Feedback System** — Users can rate the system and submit suggestions.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript, Bootstrap 4 |
| Backend | Python, Flask |
| Machine Learning | Keras, TensorFlow 2.9, OpenCV |
| NLP | NLTK, Naive Bayes Classifier |
| Speech Recognition | Google Speech Recognition API |
| Database | SQLite |
| Audio Processing | MoviePy, SpeechRecognition |

---

## Machine Learning Models

### Facial Expression Model (CNN)
- Architecture: 5 Convolutional layers, 2 Dense layers (1024 units each), Softmax output
- Input: 48x48 grayscale face images
- Classes: Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral
- Accuracy: 97%
- Face Detection: Haar Cascade Classifier (OpenCV)

### Text Classification Model (Naive Bayes)
- Training Data: Labeled positive/negative depression-related text samples
- Pipeline: Punctuation removal → Tokenization → Feature extraction → Classification
- Output: Depression Detected / No Depression Detected

---

## Project Structure

```
├── main.py                              # Flask application and all route definitions
├── supportFile.py                       # Video feed, emotion detection, model loading
├── utils.py                             # Training data loader and file export utilities
├── facial_expression_model_structure.json   # CNN architecture
├── facial_expression_model_weights.h5      # Pre-trained CNN weights
├── haarcascade_frontalface_default.xml      # Face detection classifier
├── mydatabase.db                        # SQLite database
├── templates/                           # HTML templates
├── static/                              # CSS, JS, images
├── train/                               # NLP training data (POSITIVE.txt, NEGATIVE.txt)
├── upload/                              # Uploaded video storage
└── data/                                # Extracted symptom text files
```

---

## Installation and Setup

### Prerequisites
- Python 3.9
- pip

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/depression-detection.git
cd depression-detection
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install flask==2.0.3 werkzeug==2.0.3 opencv-python pillow numpy==1.23.5
pip install pandas nltk moviepy==1.0.3 SpeechRecognition autocorrect twilio
pip install tensorflow==2.9.0
```

**4. Download NLTK data**
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

**5. Run the application**
```bash
python main.py
```

**6. Open in browser**
```
http://127.0.0.1:5000
```

---

## How to Use

1. Register an account and log in
2. Navigate to **Upload Video**
3. Upload an `.mp4` video file of the subject speaking
4. Click **Upload** to save, then **Detect Depression** to run analysis
5. The system will:
   - Stream the video and analyze facial expressions frame by frame
   - Extract audio, convert to text, and classify the speech
6. View results on the **Text Mining** page
7. Check full history under **Video History** and **Text Mining History**

---

## How Depression is Detected

```
Video Input
    |
    |---> Face Detection (Haar Cascade)
    |         |
    |         |--> Emotion Classification (CNN)
    |                   |
    |                   |--> sad/fear for 15+ frames --> Depression Detected
    |
    |---> Audio Extraction (MoviePy)
              |
              |--> Speech to Text (Google API)
                        |
                        |--> Naive Bayes Classification
                                    |
                                    |--> Depression Detected / No Depression
```

---

## Dataset

- **Facial Expressions**: FER-2013 dataset (Kaggle) — 35,887 grayscale 48x48 images across 7 emotion classes
- **Text Classification**: Custom labeled dataset of depression-related and non-depression-related text samples

---

## Limitations

- Requires a stable internet connection for Google Speech Recognition API
- Detection accuracy depends on video quality and lighting conditions
- The system is intended as a supplementary screening tool, not a clinical diagnosis
