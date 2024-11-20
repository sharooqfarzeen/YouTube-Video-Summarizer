# Streamlit app
import io
import streamlit as st
from PIL import Image

# Required modules
from video_handler import VideoHandler # Handles URL validity check, video id extraction and transcription
from summarize import get_response # Handles LLM

# Page title
st.set_page_config(page_title="YouTube Video Summarizer", page_icon="favicon.svg")

# Loading App Icon
icon_svg = open("icon.svg").read()
heading = "YT Summarizer"
# Setting header format
header = f'''
     <div style="display: flex; align-items: center;">
         <div style="margin-right: 10px;">{icon_svg}</div>
         <h1>{heading}</h1>
     </div>
     '''
# Display the icon and header
st.markdown(header, unsafe_allow_html=True)

# Initializing chat history for streamlit
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Displaying previous chat on app re-run
if st.session_state["chat_history"]:
    st.header("Current Thread")
    for message in st.session_state.chat_history:
        st.chat_message(message["role"]).write(message["content"])

# Function to refresh sidebar everytime a new title is added
def populate_sidebar():
    side_heading = "Video History"
    # Setting header format
    side_header = f'''
        <div style="display: flex; align-items: center;">
            <div style="margin-right: 10px;">{icon_svg}</div>
            <h1>{side_heading}</h1>
        </div>
        '''
    with st.sidebar:
        st.markdown(side_header, unsafe_allow_html=True)
        for title, url in st.session_state.titles:
            st.markdown(f"**[{title}]({url})**")

# Initializing titles to store video title history
# Also initiating sidebar
if "titles" not in st.session_state:
    st.session_state.titles = []
    populate_sidebar()


# Function to write to streamlit app and store to chat history
def write(message, role):
    # Display message
    st.chat_message(role).write(message)
    # Store in streamlit chat history
    st.session_state.chat_history.append({"role": role, "content": message})

# Function to fetch and display summary given a URL
def show_summary(url):
    # Initiate Video Handler Object with the "URL"
    video = VideoHandler(url)
    # If it is not a valid YouTube URL
    if not video.is_valid_youtube_url():
        # Showing user input to UI
        write(message=url, role="user")
        write(message = "Please enter a valid YouTube video URL.", role="assistant")
    # URL is valid
    else:
        # Extract video id - video_id will be set to None if not accessible
        video.extract_video_id()
        # If video was not accessible
        if not video.video_id:
            write("Please enter a publicly accessible YouTube video URL.", role="assistant")
        # If video was accessible
        else:
            with st.spinner("Processing Video..."):
                prompt = []
                # Get video title and thumbnail, if available
                video.get_title_thumbnail()
                # If thumbnail was available  
                if video.thumbnail:
                    # Saving as Image for UI rendition
                    image = Image.open(io.BytesIO(video.thumbnail))
                    # Add to prompt
                    prompt.append(image)
                    #Showing in UI
                    write(message=image, role="user")
                else:
                    write(message="Thumbnail unavailable", role="assistant")
                # If title was available
                if video.title:
                    st.session_state.titles.append((video.title, url))
                    # Adding to prompt
                    prompt.append("Video Title: " + video.title)
                    # Displating in UI
                    write(message=video.title, role="user")  
                else:
                    st.session_state.titles.append(("Title Unavailable", url))
                    write(message="Title Unavailable", role="assistant")

            with st.spinner("Fetching Transcript..."):             
                # Generate transcript
                video.get_transcript()
            # If a transcript was not available
            if not video.transcript:
                write(message="Transcript not available for the video. Please try another URL.", role="assistant")
            else:
                prompt.append(video.transcript)
                with st.spinner("Summarizing..."):
                    # Streaming summary from model and writing it to UI
                    response = st.chat_message("assistant").write_stream(get_response(prompt))
                # Adding response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})


# Chat input
text = st.chat_input(placeholder="Paste a video URL or ask follow-up questions.")

# User has entered a text
if text:
    # If this is the first run of the app
    if not st.session_state["chat_history"]:
        # Check if text is a valid URL and show summary
        show_summary(text)
    # For subsequent runs
    else:
        # If text input is a follow-up question to the summary
        if not VideoHandler(text).is_valid_youtube_url():
            write(message=text, role="user")
            with st.spinner("Fetching response..."):
                # Streaming response from model and writing it to UI
                response = st.chat_message("assistant").write_stream(get_response(text))
            # Adding response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # If input is a new video URL
        else:
            show_summary(text)
    
    populate_sidebar()