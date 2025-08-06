Live Demo: https://ai-meeting-assistant-k5l1.onrender.com/


✨ Key Features

Accurate Speech-to-Text using OpenAI's Whisper model

AI-Powered Summaries with GPT-3.5-turbo

Action Item Extraction (identifies tasks/deadlines)

Multi-Speaker Support (basic speaker differentiation)

Export Options (TXT, PDF, or copy to clipboard)

🛠️ Tech Stack

Component	Technology
Backend	Python, Flask
AI Models	OpenAI Whisper + GPT-3.5
Frontend	HTML5, CSS3, JavaScript
Deployment	Render (Free Tier)
Audio Processing	PyAudio, FFmpeg

🚀 Quick Setup

Prerequisites
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

# 3. Set up environment variables
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 4. Run the app
flask run
Visit http://localhost:5000 to use the app locally!

🔍 How It Works
User Uploads audio file (MP3/WAV) or records directly

Whisper Model converts speech to text with timestamps

Model Processes the transcript to:

Generate a concise summary

Extract action items (tasks/owners/deadlines)

Identify key discussion topics

Results Displayed in an interactive dashboard
