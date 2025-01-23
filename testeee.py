import streamlit as st
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

def transcribe_audio(audio_value):
    """Transcribe audio using WhisperTurboV3."""
    try:
        files = {"file": audio_value}
        response = requests.post(WHISPER_API_URL, headers=headers, files=files)
        response.raise_for_status()
        return response.json().get("text", "Could not retrieve text.")
    except requests.RequestException as e:
        st.error(f"Error transcribing audio: {e}")
        return None

def display_chat_message(role, content):
    """Display a chat message on the Streamlit app."""
    if role == "user":
        st.markdown(f'<div style="background-color:#e0e0e0; border-radius:10px; padding:10px; margin-bottom:5px; text-align:right;">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color:#d1ffd1; border-radius:10px; padding:10px; margin-bottom:5px;">{content}</div>', unsafe_allow_html=True)

def get_chatbot_response_openai(messages):
    """Get chatbot response using OpenAI."""
    try:
        chat_completion = openai.chat.completions.create(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=messages
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting chatbot response: {e}")
        return None

# Load environment variables
load_dotenv()

# DeepInfra API settings
WHISPER_API_URL = "https://api.deepinfra.com/v1/whisperturbov3"
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

headers = {
    "Authorization": f"Bearer {DEEPINFRA_API_KEY}"
}

# Create OpenAI client
openai = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.deepinfra.com/v1/openai"
)

# Streamlit App
st.set_page_config(page_title="Chatbot with Speech-to-Text", page_icon=":robot_face:", layout="wide")
st.title("Chatbot with Speech-to-Text and Text Input")
st.write("Talk to the chatbot using your voice or by typing your queries!")

# Sidebar instructions
st.sidebar.header("Instructions")
st.sidebar.write("""
1. Record your query or type it in the input box.
2. Use WhisperTurboV3 for audio transcription.
3. Get chatbot responses powered by OpenAI LLaMA 3.2.
""")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for message in st.session_state["messages"]:
    display_chat_message(message["role"], message["content"])

# Audio recording layout
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("Type your query here:")
with col2:
    audio_value = st.audio_input("Record a voice message")

# Handle audio input
if audio_value:
    transcription = transcribe_audio(audio_value)

    if transcription:
        st.session_state["messages"].append({"role": "user", "content": transcription})
        display_chat_message("user", transcription)

        # Get chatbot response
        messages = [
            {"role": "system", "content": "Respond like a Michelin-starred chef."},
            {"role": "user", "content": transcription}
        ]
        response = get_chatbot_response_openai(messages)
        if response:
            st.session_state["messages"].append({"role": "assistant", "content": response})
            display_chat_message("assistant", response)

# Handle text input query
if user_input:
    if st.button("Send"):
        st.session_state["messages"].append({"role": "user", "content": user_input})
        display_chat_message("user", user_input)

        # Get chatbot response
        messages = [
            {"role": "system", "content": "Respond like a Michelin-starred chef."},
            {"role": "user", "content": user_input}
        ]
        response = get_chatbot_response_openai(messages)
        if response:
            st.session_state["messages"].append({"role": "assistant", "content": response})
            display_chat_message("assistant", response)

# Clear chat history
if st.sidebar.button("Clear Chat"):
    st.session_state["messages"] = []
