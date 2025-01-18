import tempfile
import os
import openai
from dotenv import load_dotenv
from autogen import ConversableAgent
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
from io import BytesIO

# Load environment variables from .env file
load_dotenv()  # This loads the .env file, automatically detecting it in the root folder

# Set OpenAI API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')  # Get the API key from the .env file

# Sidebar Layout (Column 1 for logo, company, and developers' names)
with st.sidebar:
    st.image("logo1.jpg", width=150)  # Adjust the width of the logo
    st.markdown("""
        # Powered by Aibytec 
        Developers: Anum Zeeshan & Sabahat Shakeel
    """)

# Main Layout (Column 2 for the rest of the app content)
col1, col2 = st.columns([1, 5])  # 1:5 ratio for sidebar to content

def main():
    # Initialize session state variables if they don't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # Initialize chat history as an empty list
    
    with col2:
        # Streamlit App Title
        st.title('🎤 :blue[Voice-based Conversational Agents] 💬🤖')

        # Define the LLM configuration
        llm_config = {"model": "gpt-3.5-turbo", "max_tokens": 50}  # Limit responses to 50 tokens

        # Create Conversable Agents
        Agent_1 = ConversableAgent(
            name="smartless",
            system_message=(
                "Your name is smartless and you are a comedic personality. "
                "Keep your responses short, witty, and humorous. Focus on entertaining the audience with brief jokes."
                "Keep your responses under 50 words."
            ),
            llm_config=llm_config,
            human_input_mode="NEVER"
        )

        Agent_2 = ConversableAgent(
            name="Huberman-Lab",
            system_message=(
                "Your name is Huberman-Lab and you are a knowledgeable Tech Agent. "
                "Provide short, concise, and informative responses. Focus on keeping the conversation informative but succinct."
                "Keep your responses under 50 words."
            ),
            llm_config=llm_config,
            human_input_mode="NEVER"
        )

        # Handle the audio input and response
        st.subheader('Voice Interaction')

        # Record audio input from the user
        audio_bytes = audio_recorder(
            energy_threshold=0.01,
            pause_threshold=0.8,
            text="Speak now...max 5 min",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_name="microphone",
            icon_size="2x"
        )

        if audio_bytes:
            # Convert audio to text using speech-to-text
            user_input = speech_to_text(audio_bytes)
            st.session_state.chat_history.append({"role": "user", "message": user_input})
            
            # Generate AI response based on the conversation context
            chat_result = Agent_1.initiate_chat(
                recipient=Agent_2,
                message=user_input,
                max_turns=2
            )
            
            if chat_result is None:
                st.error("Error: No chat history returned. Please check the ConversableAgent configuration.")
            else:
                response = chat_result.chat_history[-1]['content']
                # Convert the AI response text to speech using gTTS
                audio_response = gTTS(response, lang="en")
                
                # Save the audio response to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                    audio_response.save(temp_audio_file.name)
                    temp_audio_file_path = temp_audio_file.name
                
                # Play the AI response as audio
                st.audio(temp_audio_file_path, format="audio/mp3", autoplay=True)

                # Append AI response to the chat history
                st.session_state.chat_history.append({"role": "AI", "message": response})

        # Display conversation history (text + audio)
        if "chat_history" in st.session_state:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["message"])
                elif message["role"] == "AI":
                    with st.chat_message("AI"):
                        st.write(message["message"])
                        st.audio(temp_audio_file_path, format="audio/mp3", autoplay=False)

def speech_to_text(audio_bytes):
    """Convert audio bytes to text using a speech-to-text model."""
    # This is a placeholder; you can integrate any speech-to-text service (like Google Speech API, Whisper, etc.)
    return "This is a placeholder for user speech input."

if _name_ == "_main_":
    main()
