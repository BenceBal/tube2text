document.addEventListener('DOMContentLoaded', function() {
  const btn = document.getElementById('summarize-btn');
  const output = document.getElementById('output');

  btn.addEventListener('click', async () => {
    output.innerText = "Processing...";
    btn.disabled = true;

    // Get current tab URL
    chrome.tabs.query({active: true, currentWindow: true}, async function(tabs) {
      const url = new URL(tabs[0].url);
      const videoId = url.searchParams.get("v");

      if (!videoId) {
        output.innerText = "Error: Not a YouTube video page.";
        btn.disabled = false;
        return;
      }

      try {
        const response = await fetch("http://localhost:8000/summarize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ video_id: videoId })
        });

        if (!response.ok) {
          throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();
        output.innerText = data.summary; // Simple text render (Markdown TODO)
      } catch (error) {
        output.innerText = "Error: Backend unreachable. Is server.py running?\n" + error.message;
      } finally {
        btn.disabled = false;
      }
    });
  });
});