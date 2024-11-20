import os
import re
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

# Handles URL validity check, video id extraction and transcription
class VideoHandler:

    def __init__(self, url):
        self.url = url # Video URL
        self.video_id = None # Video ID
        self.title = None # YouTube video title
        self.thumbnail = None # YouTube thumbnail
        self.transcript = None # Video transcript

    # Function to check if URL is a valid YouTube address
    def is_valid_youtube_url(self):
        # Regex pattern to check for a valid YouTube URL
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        
        match = youtube_regex.match(self.url)
        return match is not None

    # Function to extract video id from URL
    def extract_video_id(self):
        # Regex to match video ID
        video_id_match = re.search(r"(?:v=|\/v\/|\/embed\/|youtu\.be\/|\/shorts\/|\/watch\?v=|\/videos\/|\/e\/)([^#\&\?]{11})", self.url)
        
        if video_id_match:
            self.video_id = video_id_match.group(1)
        else:
            self.video_id = None

    # Function to extract video title and thumbnail, if available
    def get_title_thumbnail(self):
        # Fetch the YouTube page
        response = requests.get(self.url)
        
        # Check if the request was successful
        if response.status_code != 200:
            self.title = None
            self.thumbnail = None
            return

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the video title
        # Find the <meta> tag with name "title"
        meta_title_tag = soup.find('meta', attrs={'name': 'title'})
        self.title = meta_title_tag["content"] if meta_title_tag else None

        # Construct thumbnail URL
        thumbnail_url = f"https://img.youtube.com/vi/{self.video_id}/maxresdefault.jpg"

        response = requests.get(thumbnail_url)

        # Save the image if the request was successful
        self.thumbnail = response.content if (response.status_code == 200) else None

    # Function to retrieve transcript
    def get_transcript(self):
        try:
            language_list = ["en", "en-US", "en-GB", "en-IN", "en-AU", "en-CA", "en-NZ", "en-ZA", "en-PH", 
                            "en-SG", "en-JM", "en-NG", "en-HK", "en-TT", "en-BZ", "en-MY", "en-IE"]
            transcript = YouTubeTranscriptApi.get_transcript(video_id=self.video_id, languages=language_list)
            self.transcript = str(transcript)
        except:
            self.transcript = None