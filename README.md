# Tube2Text - Private YouTube Summarizer 📺🤖

A lightweight, privacy-focused Chrome Extension that summarizes YouTube videos using your own local LLM backend.

**Why?**
Most "AI Summarizers" are paid SaaS tools that harvest your data. This one runs on your own hardware (or cloud VPS), uses your own API key, and costs pennies per video.

## 🏗 Architecture

1.  **Frontend (Extension):** A simple Chrome popup that extracts the Video ID from the current tab.
2.  **Backend (Python):** A FastAPI server that fetches the transcript (via `youtube-transcript-api`) and summarizes it with GPT-4o.

## 🚀 Setup Guide

### Part 1: The Backend (Server)

Run this on your local machine, Raspberry Pi, or VPS.

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/BenceBal/tube2text.git
    cd tube2text/backend
    ```

2.  **Install Dependencies:**
    ```bash
    pip install fastapi uvicorn youtube-transcript-api openai
    ```

3.  **Set your API Key:**
    ```bash
    export OPENAI_API_KEY="sk-..."
    ```

4.  **Run the Server:**
    ```bash
    python3 server.py
    ```
    *The server will start on `0.0.0.0:8000`.*

### Part 2: The Frontend (Extension)

1.  **Go to Chrome Extensions:**
    *   Open `chrome://extensions/` in your browser.
    *   Toggle **Developer mode** (top right).

2.  **Load the Extension:**
    *   Click **Load unpacked**.
    *   Select the `extension` folder from this repo.

3.  **Configuration (Optional):**
    *   By default, the extension connects to `http://localhost:8000`.
    *   If your backend is running on a different machine (e.g., a Raspberry Pi), edit `extension/popup.js`:
        ```javascript
        // Change this line:
        const response = await fetch("http://<YOUR_SERVER_IP>:8000/summarize", { ...
        ```
    *   Click the "Refresh" icon on the extension card in `chrome://extensions/` after saving changes.

## 🎮 Usage

1.  Open any YouTube video.
2.  Click the **Tube2Text** icon in your toolbar.
3.  Click **"Summarize Video"**.
4.  Wait a few seconds for the transcript to be processed and summarized.

## 🛠 Troubleshooting

-   **"Error: Backend unreachable":** Ensure `server.py` is running and the URL in `popup.js` matches your server's IP.
-   **"Error: Not a YouTube video":** Ensure you are on a video page (`youtube.com/watch?v=...`).
-   **Transcript Errors:** Some videos have disabled captions. The backend will log this error.

## 📜 License
MIT
