import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# ==========================================
# CONFIGURATION
# ==========================================
YOUTUBE_API_KEY = "AIzaSyCoGk7Y0wWsBeO8N0VAUNBXn7Hu5XzBuhI"

# Initialize YouTube API Client
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# List of your experts and specific targeted search phrases
EXPERTS = {
    "alex-berman": "Alex Berman sales cold email",
    "jason-bay": "Jason Bay Outbound Squad sales",
    "morgan-j-ingram": "Morgan J Ingram sales prospecting",
    "will-allred": "Will Allred Lavender cold email",
    "armand-farrokh": "Armand Farrokh 30MPC sales", 
    "nick-cegelski": "Nick Cegelski 30MPC cold calling",   
    "jeremy-chatelaine": "Jeremy Chatelaine QuickMail sales",
    "justin-rowe": "Justin Rowe Impactable LinkedIn ads",
    "belal-batrawy": "Belal Batrawy Death to Fluff sales",
    "kyle-coleman": "Kyle Coleman Clari sales growth"
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_latest_videos(search_query, max_results=5):
    """Queries YouTube search directly for the expert's name to grab videos."""
    try:
        request = youtube.search().list(
            part="snippet",
            q=search_query,
            maxResults=max_results,
            type="video",
            order="date"
        )
        response = request.execute()
        videos = []
        for item in response.get("items", []):
            videos.append({
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"]
            })
        return videos
    except Exception as e:
        print(f"Error searching for '{search_query}': {e}", flush=True)
        return []

def get_transcript(video_id):
    """A bulletproof transcript scraper that explicitly loops through all available English fragments."""
    try:
        # Fetch the master list of all caption tracks available on YouTube's servers for this specific video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Look specifically for any track containing 'en' (Manual or Auto-Generated)
        try:
            transcript = transcript_list.find_transcript(['en'])
            full_text = " ".join([line["text"] for line in transcript.fetch()])
            return full_text
        except Exception:
            # Fallback: Loop over the available tracks and grab the first track regardless of region string
            for track in transcript_list:
                if 'en' in track.language_code.lower():
                    full_text = " ".join([line["text"] for line in track.fetch()])
                    return full_text
            return None
    except Exception:
        return None

# ==========================================
# MAIN EXECUTION LOOP
# ==========================================

def main():
    print("🚀 Starting portfolio transcript downloader...", flush=True)
    
    for expert_name, search_query in EXPERTS.items():
        print(f"\n--- Processing Expert: {expert_name} ---", flush=True)
        
        output_dir = f"research/youtube-transcripts/{expert_name}"
        
        # Ensure the directories exist safely
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except FileExistsError:
                pass 
        
        videos = get_latest_videos(search_query, max_results=5)
        print(f"Found {len(videos)} recent videos for {expert_name}.", flush=True)
        
        for video in videos:
            v_id = video["id"]
            v_title = video["title"]
            
            # Form clean windows legal filenames
            safe_title = "".join([c for c in v_title if c.isalnum() or c==' ']).rstrip()
            safe_title = safe_title.replace(" ", "_").lower()[:50]
            filename = f"{output_dir}/{safe_title}.md"
            
            if os.path.exists(filename):
                print(f"  ➜ Already downloaded: {v_title}", flush=True)
                continue
                
            print(f"  🎬 Downloading transcript for: {v_title} ({v_id})", flush=True)
            
            transcript = get_transcript(v_id)
            if not transcript:
                print(f"    ⚠️ No transcript tracks readable. Skipping.", flush=True)
                continue 
                
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"# {v_title}\n\n")
                    f.write(f"**Video ID:** {v_id}\n\n")
                    f.write("## Raw Transcript\n")
                    f.write(transcript)
                print(f"    ✓ Saved text to {filename}", flush=True)
            except Exception as e:
                print(f"    ❌ Failed to save file: {e}", flush=True)

if __name__ == "__main__":
    main()


