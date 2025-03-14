import re
from typing import Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:v=|v/|embed/|youtu.be/)([^&?#]+)',
        r'(?:youtube.com/|youtu.be/)(?:watch\?v=)?([^&?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def get_transcript(video_id: str, language: Optional[str] = None) -> Tuple[str, str, list]:
    """
    Fetch and format transcript in both timestamped and clean versions.
    Returns tuple of (timestamped_transcript, clean_transcript, available_languages)
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list_transcripts(video_id)
        
        # Get available languages
        available_languages = [
            (t.language_code, t.language) 
            for t in transcript_list
        ]
        
        # Get transcript in requested language or default
        if language:
            transcript = transcript_list.find_transcript([language])
        else:
            transcript = transcript_list.find_transcript([t[0] for t in available_languages])
            
        fetched_transcript = transcript.fetch()
        
        # Format timestamped version
        timestamped_lines = []
        for entry in fetched_transcript:
            timestamp = format_timestamp(entry.start)
            timestamped_lines.append(f"[{timestamp}] {entry.text}")
        timestamped_transcript = "\n".join(timestamped_lines)
        
        # Get clean version using TextFormatter
        formatter = TextFormatter()
        clean_transcript = formatter.format_transcript(fetched_transcript)
        
        return timestamped_transcript, clean_transcript, available_languages
        
    except Exception as e:
        raise Exception(f"Error fetching transcript: {str(e)}")
