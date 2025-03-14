import re
import os
import requests
from typing import Optional, Tuple

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
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_transcript(video_id: str, language: Optional[str] = None) -> Tuple[str, str, list]:
    """
    Fetch transcript using Supadata API.
    Returns tuple of (timestamped_transcript, clean_transcript, available_languages)
    """
    api_key = os.getenv('SUPADATA_API_KEY')
    if not api_key:
        raise Exception("Supadata API key not found")

    # Base API URL
    base_url = "https://api.supadata.ai/v1/youtube/transcript"

    # Prepare headers
    headers = {
        'x-api-key': api_key
    }

    # Prepare params
    params = {
        'url': f'https://www.youtube.com/watch?v={video_id}',
        'text': 'false'  # Get full transcript with timestamps first
    }

    if language:
        params['lang'] = language

    try:
        # Make API request
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Format timestamped transcript
        timestamped_lines = []
        for segment in data['content']:
            timestamp = format_timestamp(segment['offset'] / 1000)  # Convert ms to seconds
            timestamped_lines.append(f"[{timestamp}] {segment['text']}")
        timestamped_transcript = "\n".join(timestamped_lines)

        # Get clean transcript (text only)
        params['text'] = 'true'
        text_response = requests.get(base_url, headers=headers, params=params)
        text_response.raise_for_status()
        clean_transcript = text_response.json()['content']

        # Get available languages
        available_languages = [
            (lang, lang) for lang in data.get('availableLangs', [])
        ]

        return timestamped_transcript, clean_transcript, available_languages

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching transcript: {str(e)}")