import os
from typing import Dict, List, Any, Optional
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from base_agent import BaseAgent


class YoutubeAgent(BaseAgent):
    """Agent specialized for searching YouTube and processing video transcripts."""
    
    def __init__(self):
        super().__init__("YouTube Agent")
        self.youtube_api_key = os.getenv("GOOGLE_API_KEY")  # Same key for YouTube API
        if not self.youtube_api_key:
            raise ValueError("YouTube API key not found")
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search YouTube for videos."""
        max_results = kwargs.get('max_results', 5)
        
        youtube = build("youtube", "v3", developerKey=self.youtube_api_key)
        
        try:
            request = youtube.search().list(
                q=query,
                part="snippet",
                type="video",
                maxResults=max_results,
                safeSearch="none"
            )
            response = request.execute()
            
            videos = []
            for item in response.get("items", []):
                videos.append({
                    "videoId": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "channelTitle": item["snippet"]["channelTitle"],
                    "publishTime": item["snippet"].get("publishTime"),
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    "source_type": "youtube"
                })
            return videos
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []
    
    def process_sources(self, sources: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Process YouTube sources by fetching transcripts."""
        char_limit = kwargs.get('transcript_limit', 3000)
        
        for video in sources:
            video['transcript'] = self._fetch_transcript(video['videoId'], char_limit)
        
        return sources
    
    def _fetch_transcript(self, video_id: str, char_limit: int = 3000) -> Optional[str]:
        """Fetch transcript for a video."""
        try:
            transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=['en'])
            texts = [seg.text.strip() for seg in transcript_list if hasattr(seg, 'text') and seg.text]
            joined = " ".join(texts)
            
            if len(joined) > char_limit:
                joined = joined[:char_limit] + "..."
            return joined
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception:
            return None