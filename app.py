from flask import Flask, render_template, request, jsonify
import os, json
from datetime import datetime
import requests
import base64
from dotenv import load_dotenv
import shutil
from werkzeug.utils import secure_filename
from pydub import AudioSegment

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
HISTORY_FILE = 'history.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENROUTER_API_KEY')
HF_TOKEN = os.getenv('HF_API_TOKEN')

# Validate API keys on startup
if not API_KEY or not HF_TOKEN:
    raise ValueError("Missing required API keys. Please check your .env file")

# Language code mapping
LANGUAGE_MAP = {
    'english': 'en',
    'spanish': 'es',
    'zulu': 'zu',
    'afrikaans': 'af',
    'german': 'de'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/process', methods=['POST'])
def process_audio():
    if 'audioFile' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
        
    file = request.files['audioFile']
    target_lang = request.form.get('targetLanguage', 'english')  # default to english
    target_lang_code = LANGUAGE_MAP.get(target_lang.lower(), 'en')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Step 1: Transcribe
        transcription = transcribe_audio(filepath)
        if "failed" in transcription.lower():
            return jsonify({"error": "Transcription failed", "details": transcription}), 500

        # Step 2: Summarize
        summary = "Summarization failed."
        bullets = []
        try:
            summary, bullets = summarize_text(transcription)
        except Exception as e:
            print(f"⚠️ Summarization error: {str(e)}")

        # Step 3: Translate
        translation = "Translation failed."
        if summary and summary != "Summarization failed.":
            try:
                translation = translate_text(summary, target_lang_code)
            except Exception as e:
                print(f"⚠️ Translation error: {str(e)}")

        # Save to history
        save_to_history(filename, transcription, summary, bullets, translation)

        return jsonify({
            "filename": filename,
            "audio_url": f"/static/audio/{filename}",
            "transcription": transcription,
            "summary": summary,
            "bullets": bullets,
            "translation": translation
        })

    except Exception as e:
        print(f"❌ Processing error: {str(e)}")
        return jsonify({"error": "Processing failed", "details": str(e)}), 500
    finally:
        # Clean up the uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)

def transcribe_audio(filepath):
    try:
        # Determine content type based on file extension
        ext = os.path.splitext(filepath)[1].lower()
        content_type = {
            '.flac': 'audio/flac',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.m4a': 'audio/m4a',
            '.amr': 'audio/amr',
            '.webm': 'audio/webm'
        }.get(ext, 'audio/mpeg')  # default to mp3

        API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": content_type
        }

        with open(filepath, 'rb') as f:
            response = requests.post(
                API_URL,
                headers=headers,
                data=f,
                timeout=30
            )

        print(f"Transcription API response: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            return response.json().get("text", "No transcription text returned")
        elif response.status_code == 503:
            return "Model is loading, please try again in a few seconds"
        else:
            error_msg = response.json().get("error", response.text)
            return f"Transcription API error {response.status_code}: {error_msg}"

    except Exception as e:
        return f"Transcription processing error: {str(e)}"

def summarize_text(text):
    if not text.strip():
        return "No text to summarize", []
        
    prompt = f"""Please summarize the following text and provide key points as bullet points:
    
    Text:
    {text}
    
    Summary:
    Key points:
    - """
    
    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=data,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Split into summary and bullets
        parts = content.split('Key points:')
        summary = parts[0].strip()
        bullets = []
        
        if len(parts) > 1:
            bullet_points = parts[1].split('\n')
            bullets = [bp.strip('-• ') for bp in bullet_points if bp.strip()]
        
        return summary, bullets

    except Exception as e:
        print(f"Summarization error: {str(e)}")
        return f"Summarization failed: {str(e)}", []

def translate_text(text, target_lang):
    if not text.strip() or text == "Summarization failed.":
        return "Nothing to translate"
        
    prompt = f"""Translate the following text to {target_lang}. 
    Maintain the original meaning and tone:
    
    {text}"""
    
    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=data,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return f"Translation failed: {str(e)}"

def save_to_history(filename, transcription, summary, bullets, translation):
    # Create audio directory if it doesn't exist
    audio_dir = os.path.join('static', 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    
    # Save the audio file permanently
    temp_audio_path = os.path.join(UPLOAD_FOLDER, filename)
    permanent_audio_path = os.path.join(audio_dir, filename)
    
    if os.path.exists(temp_audio_path):
        shutil.move(temp_audio_path, permanent_audio_path)

    entry = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "filename": filename,
        "audio_url": f"/static/audio/{filename}",
        "transcription": transcription,
        "summary": summary,
        "bullets": bullets,
        "translation": translation
    }
    
    try:
        with open(HISTORY_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Failed to save history: {str(e)}")

@app.route('/get-history')
def get_history():
    try:
        with open(HISTORY_FILE, 'r') as f:
            # Read lines in reverse to show newest first
            lines = f.readlines()
            history = [json.loads(line) for line in lines if line.strip()]
            return jsonify(history[::-1])  # Reverse to show newest first
    except FileNotFoundError:
        return jsonify([])
    except Exception as e:
        print(f"Error reading history: {str(e)}")
        return jsonify([])

@app.route('/delete-history', methods=['POST'])
def delete_history():
    data = request.get_json()
    filename = data.get('filename')
    timestamp = data.get('timestamp')

    if not filename or not timestamp:
        return jsonify({"error": "Missing filename or timestamp"}), 400

    try:
        entries = []
        with open(HISTORY_FILE, 'r') as f:
            for line in f:
                entry = json.loads(line)
                # Keep all except the one to delete (match by filename + timestamp)
                if not (entry.get('filename') == filename and entry.get('timestamp') == timestamp):
                    entries.append(entry)

        # Rewrite file with remaining entries
        with open(HISTORY_FILE, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        # Also delete the audio file
        audio_path = os.path.join('static', 'audio', filename)
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return jsonify({"message": "Deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)