import os
import logging
import streamlit as st

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Configure logging to write to a file, set level to ERROR to log only errors
logging.basicConfig(filename='error.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def start_chat_session():
    # Fetching the API KEY
    if "GOOGLE_API_KEY" in st.session_state:
        genai.configure(api_key=st.session_state["GOOGLE_API_KEY"])

    # Initializing model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                system_instruction=
                                """
                                You are a YouTube video transcript summarizer. You will get 2 types of inputs.
                                
                                First type of input will have 3 parameters:
                                    1. The YouTube video title
                                    2. The video thumbnail, which is an image
                                    3. The video transcript
                                    
                                    The YouTube video transcripts will be in the following format:
                                    [{'text': "",
                                    'start': ,
                                    'duration':},
                                    .
                                    .
                                    .
                                    ]
                                    
                                    Your job is to go through the video title, thumbnail and transcript to form a summary of the video.
                                    The length of the summary should be directly proportional to video length.
                                    The sentiment and style of summary should reflect the topic of the video and should sound like a human.
                                
                                Second type of input will have a single parameter. 
                                    They may be user follow ups for previous summaries. Such promps will only have a single text input.
                                    Provide answers to such follow-up queries using previous chat history.
                                """)

    chat = model.start_chat()

    return chat

def get_response(prompt, chat):
    try:
        # Fetching response
        response = chat.send_message(
            prompt, stream=True, 
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
    }
    )
        # Stream response
        for chunk in response:
            yield chunk.text   
    except Exception as e:
        
        # Logging the error
        logging.error(str(e), exc_info=True)

        error_msg = ["\n", "\n", "Query/URL", "not", "supported."]
        
        for word in error_msg:
            yield word + " "