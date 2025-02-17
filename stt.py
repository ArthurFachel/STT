from openai import OpenAI
import streamlit as st
import io
st.title("Geo Malta")

client = OpenAI(
    api_key=st.secrets["DEEPINFRA_TOKEN"], 
    base_url="https://api.deepinfra.com/v1/openai"
)

def add_custom_css():
    st.markdown(
        """
        <style>
        .user-message {
            background-color: #e0e0e0;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 5px;
            text-align: right;
        }
        .assistant-message {
            background-color: #d1ffd1;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

add_custom_css()

#Instructions 
st.sidebar.header("Instructions")
st.sidebar.write("""
1. Faça Sua Pergunta  
   - Digite sua pergunta na barra de texto ou use o botão de gravação de áudio.  
   - Para gravar, clique no microfone, fale sua pergunta e espere a transcrição aparecer no chat.  
   - Exemplos:  
       - "Quais fósseis existem na Formação Santana?"  
       - "O que é um afloramento?"

2. Receba a Resposta  
   - A IA responderá no campo de chat com explicações simples e claras sobre geologia e paleontologia da Bacia do Araripe.
""")

if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.columns([4, 1])

with col1:
    inputtext = st.text_input("Digite sua pergunta aqui:")

for message in st.session_state.messages:
    css_class = "user-message" if message["role"] == "user" else "assistant-message"
    st.markdown(f'<div class="{css_class}">{message["content"]}</div>', unsafe_allow_html=True)

with col2:
    audio_file = st.audio_input("Record")

def transcribe_audio(file):
    # Devagar 
    #ja tentei alterar de .wav para mp3, sem sucesso

    import io
    from pydub import AudioSegment

    audio_stream = file.read()
    audio_format = file.name.split('.')[-1].lower()
    
    if audio_format != 'mp3':
        audio = AudioSegment.from_file(io.BytesIO(audio_stream), format=audio_format)
        mp3_audio = io.BytesIO()
        audio.export(mp3_audio, format="mp3")
        mp3_audio.seek(0)
        audio_stream = mp3_audio.read()
    
    transcription = client.audio.transcriptions.create(
        model="openai/whisper-large-v3-turbo",
        file=io.BytesIO(audio_stream),
    )

    return transcription.text

if audio_file:
    with st.spinner("Transcribing audio..."):
        transcribed_text = transcribe_audio(audio_file)
    
    # Display the transcribed text as a user message
    st.session_state.messages.append({"role": "user", "content": transcribed_text})
    st.markdown(f'<div class="user-message">{transcribed_text}</div>', unsafe_allow_html=True)

    with st.spinner("Generating response..."):
        # Generate a response using the transcribed text
        completion = client.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            prompt=f'<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{transcribed_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n',
            stop=['<|eot_id|>'],
            stream=True,
        )

        response_text = ""
        for event in completion:
            if not event.choices[0].finish_reason:
                response_text += event.choices[0].text

        
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.markdown(f'<div class="assistant-message">{response_text}</div>', unsafe_allow_html=True)


#Userinput
if inputtext:
    st.session_state.messages.append({"role": "user", "content": inputtext})
    st.markdown(f'<div class="user-message">{inputtext}</div>', unsafe_allow_html=True)

    with st.spinner("Generating response..."):
        completion = client.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            prompt=f'<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{inputtext}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n',
            stop=['<|eot_id|>'],
            stream=True,
        )

        response_text = ""
        for event in completion:
            if not event.choices[0].finish_reason:
                response_text += event.choices[0].text

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.markdown(f'<div class="assistant-message">{response_text}</div>', unsafe_allow_html=True)
        inputtext = ""
