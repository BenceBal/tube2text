from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
from openai import OpenAI
import os
import json

app = FastAPI()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class VideoRequest(BaseModel):
    video_id: str

def fetch_transcript_ytdlp(video_id):
    """
    Robust transcript fetching using yt-dlp.
    Downloads subtitles to memory/temp file and parses them.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'outtmpl': '/tmp/%(id)s', # Linux/Mac path. Windows uses tempdir.
        'quiet': True,
        'no_warnings': True
    }
    
    # On Windows, adjust temp path
    if os.name == 'nt':
        ydl_opts['outtmpl'] = '%(id)s' 

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Find subtitle URL
            subs = info.get('subtitles') or info.get('automatic_captions')
            if not subs or 'en' not in subs:
                raise Exception("No English subtitles found.")
            
            # Get the first available format (usually json3 or vtt)
            sub_url = subs['en'][0]['url']
            
            # Fetch the actual subtitle content
            import requests
            res = requests.get(sub_url)
            
            # Simple parsing (JSON3 format often returned by YouTube internal API)
            try:
                data = res.json()
                text_parts = []
                if 'events' in data:
                    for event in data['events']:
                        if 'segs' in event:
                            for seg in event['segs']:
                                if 'utf8' in seg:
                                    text_parts.append(seg['utf8'])
                return " ".join(text_parts)
            except:
                # Fallback: Just return raw text if JSON parse fails (VTT/SRT)
                return res.text

    except Exception as e:
        print(f"[!] yt-dlp error: {e}")
        raise e

@app.post("/summarize")
async def summarize_video(request: VideoRequest):
    print(f"[*] Fetching transcript for video: {request.video_id}")
    
    try:
        # 1. Fetch
        full_text = fetch_transcript_ytdlp(request.video_id)
        
        # Truncate
        if len(full_text) > 15000:
            full_text = full_text[:15000] + "... [Truncated]"

        # 2. Summarize
        print("[*] Sending to LLM...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a YouTube Summary Expert. Extract key takeaways. Be concise."},
                {"role": "user", "content": full_text}
            ]
        )
        return {"summary": response.choices[0].message.content}

    except Exception as e:
        print(f"[!] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
