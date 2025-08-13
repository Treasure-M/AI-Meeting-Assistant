🌐 Live Demo: https://ai-meeting-assistant-k5l1.onrender.com/

✨ Key Features

Precise Speech-to-Text utilizing OpenAI's Whisper prototype.
AI-Powered summaries with mistralai/mistral-7b-instruct: free.
Action Object Extraction (recognizes tasks/deadlines).
Multi-Speaker Support (primary speaker differentiation)
Export Options (TXT, PDF, or copy to clipboard)

🛠️ Tech Stack

Component Technology
Backend	Python, Flask
AI Models	OpenAI Whisper + GPT-3.5
Frontend	HTML5, CSS3, JavaScript
Deployment	Render (Free Tier)
Audio Processing	PyAudio, FFmpeg

🚀 Quick Setup

Requirements

Python 3.10+
OpenAI API key (Get yours here)
FFmpeg (brew install ffmpeg or sudo apt install ffmpeg)

Installation

bash
# 1. Clone repository

git clone https://github.com/Treasure-M/AI-Meeting-Assistant.git
cd AI-Meeting-Assistant

# 2. Install dependencies

pip install -r requirements.txt

# 3. Appoint environment variables

echo "OPENAI_API_KEY=your_api_key_here" > .env

# 4. Execute the app

flask run
Visit http://localhost:5000 to use the app locally!

🔍 How It Operates

The user uploads an audio file (MP3/WAV) or records it directly.
Whisper Model transforms speech to text with timestamps.
Prototype Processes the transcript to:
Develop a summary.
Remove activity items (tasks/owners/deadlines).
Recognize critical conversation subjects.
Outcomes are displayed in an interactive dashboard.

