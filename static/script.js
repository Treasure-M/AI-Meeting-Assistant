// static/script.js
document.addEventListener("DOMContentLoaded", () => {
  // Sidebar toggle
  const toggleButton = document.getElementById("toggleSidebar");
  const sidebar = document.getElementById("sidebar");

  toggleButton.addEventListener("click", () => {
    sidebar.classList.toggle("closed");
  });

  // File input handling
  const fileInput = document.getElementById('fileInput');
  const uploadLabel = document.querySelector('.upload-label');

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      uploadLabel.textContent = fileInput.files[0].name;
    } else {
      uploadLabel.textContent = 'Choose File';
    }
  });

  // Audio recording functionality
  let mediaRecorder;
  let audioChunks = [];
  let recordedBlob;

  const startBtn = document.getElementById('startRecording');
  const stopBtn = document.getElementById('stopRecording');
  const uploadBtn = document.getElementById('uploadRecording');
  const playback = document.getElementById('recordingPlayback');
  
  startBtn.addEventListener('click', async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const audioURL = URL.createObjectURL(recordedBlob);
        playback.src = audioURL;
        playback.style.display = 'block';
        uploadBtn.disabled = false;
      };

      mediaRecorder.start();
      startBtn.disabled = true;
      stopBtn.disabled = false;
    } catch (error) {
      alert(`Error accessing microphone: ${error.message}`);
    }
  });

  stopBtn.addEventListener('click', () => {
    mediaRecorder.stop();
    stopBtn.disabled = true;
    startBtn.disabled = false;
  });

  uploadBtn.addEventListener('click', () => {
    const title = document.getElementById('recordingTitle').value || 'untitled';
    const language = document.querySelector('#recordUploadForm select').value;
    
    if (!language) {
      alert('Please select a target language');
      return;
    }

    const formData = new FormData();
    formData.append('audioFile', recordedBlob, `${title}.webm`);
    formData.append('targetLanguage', language);

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';

    fetch('/process', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert(`Error: ${data.error}`);
      } else {
        displayResults(data);
        loadHistory();
      }
    })
    .catch(error => {
      alert(`Upload failed: ${error.message}`);
    })
    .finally(() => {
      uploadBtn.disabled = false;
      uploadBtn.textContent = 'Upload Recording';
    });
  });

  // Drag and drop functionality
  const uploadZone = document.getElementById('uploadZone');
  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
  });

  uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
  });

  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      uploadLabel.textContent = fileInput.files[0].name;
    }
  });
});

// Global functions
function displayResults(data) {
  document.getElementById("transcriptionText").innerText = data.transcription || "No transcription available.";
  document.getElementById("summaryText").innerText = data.summary || "No summary available.";
  document.getElementById("keyPoints").innerHTML = data.bullets && data.bullets.length > 0 ?
    data.bullets.map(b => `<li>${b}</li>`).join('') :
    "<li>No key points available.</li>";
  document.getElementById("translatedText").innerText = data.translation || "No translation available.";

  const audioDownload = document.getElementById("audioDownload");
  if (data.audio_url) {
    audioDownload.href = data.audio_url;
    audioDownload.style.display = "inline-block";
    audioDownload.download = data.filename || "audio_output.mp3";
  } else {
    audioDownload.style.display = "none";
  }
}

function loadHistory() {
  fetch("/get-history")
    .then((res) => res.json())
    .then((history) => {
      const list = document.getElementById("historyList");
      list.innerHTML = "";
      if (history.length === 0) {
        list.innerHTML = "<li>No history yet</li>";
        return;
      }
      history.forEach((item) => {
        const li = document.createElement("li");
        const date = new Date(item.timestamp);
        li.textContent = `${date.toLocaleString()} - ${item.filename}`;

        const delBtn = document.createElement("button");
        delBtn.textContent = "🗑️";
        delBtn.title = "Delete this entry";
        delBtn.className = "delete-btn";

        delBtn.onclick = (e) => {
          e.stopPropagation();
          if (confirm("Delete this history entry?")) {
            fetch("/delete-history", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ filename: item.filename, timestamp: item.timestamp }),
            })
            .then(res => res.json())
            .then(data => {
              if (data.error) alert("Error: " + data.error);
              else loadHistory();
            })
            .catch(() => alert("Failed to delete entry"));
          }
        };

        li.appendChild(delBtn);
        li.onclick = () => displayHistoryItem(item);
        list.appendChild(li);
      });
    });
}

function downloadText() {
  const transcription = document.getElementById("transcriptionText").innerText;
  const summary = document.getElementById("summaryText").innerText;
  const bullets = Array.from(document.getElementById("keyPoints").children)
    .map(li => li.textContent).join("\n- ");
  const translation = document.getElementById("translatedText").innerText;

  const content = `=== Transcription ===\n${transcription}\n\n` +
                  `=== Summary ===\n${summary}\n\n` +
                  `=== Key Points ===\n- ${bullets}\n\n` +
                  `=== Translation ===\n${translation}`;

  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `meeting-summary-${new Date().toISOString().slice(0,10)}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function displayHistoryItem(item) {
  document.getElementById("transcriptionText").innerText = item.transcription || "No transcription available.";
  document.getElementById("summaryText").innerText = item.summary || "No summary available.";
  document.getElementById("keyPoints").innerHTML = item.bullets && item.bullets.length > 0 ?
    item.bullets.map(b => `<li>${b}</li>`).join('') :
    "<li>No key points available.</li>";
  document.getElementById("translatedText").innerText = item.translation || "No translation available.";

  const audioDownload = document.getElementById("audioDownload");
  if (item.audio_url) {
    audioDownload.href = item.audio_url;
    audioDownload.style.display = "inline-block";
    audioDownload.download = item.filename || "audio_output.mp3";
  } else {
    audioDownload.style.display = "none";
  }
}