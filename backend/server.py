from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os

app = FastAPI()

# --- CONFIGURATION ---
# Assumes OPENAI_API_KEY is set in environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class VideoRequest(BaseModel):
    video_id: str

@app.post("/summarize")
async def summarize_video(request: VideoRequest):
    print(f"[*] Fetching transcript for video: {request.video_id}")
    
    try:
        # 1. Get Transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(request.video_id)
        
        # Combine text chunks (limit to ~15k chars to save tokens)
        full_text = " ".join([item['text'] for item in transcript_list])
        if len(full_text) > 15000:
            full_text = full_text[:15000] + "... [Truncated]"

        # 2. Summarize with LLM
        print("[*] Sending to LLM for summary...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a YouTube Summary Expert. Extract the key takeaways, actionable insights, and distinct sections from the video transcript provided. Use bullet points and headers. Be concise."},
                {"role": "user", "content": full_text}
            ]
        )
        
        summary = response.choices[0].message.content
        return {"summary": summary}

    except Exception as e:
        print(f"[!] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
