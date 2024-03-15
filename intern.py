import gradio as gr
import openai
import os
from gtts import gTTS
from datetime import datetime
from playsound import playsound


openai.api_key = os.getenv('OPENAI_API_KEY')

messages = [{
    "role": "system",
    "content": 'Jij bent onze stagaire voor de Data Lounge Podcast. Jij bent een grappige en snuggere\
                        jongedame en jouw naam is Jadselien. Vandaag doen we een test voor de eerste opname.\
                        het is belangrijk dat je enthousiast bent en dat je af een toe eens een scherp grapje maakt\
                        je doet deze podcast samen met mij, (Huub) en Jago'
}]


def transcribe(audio):
    global messages

    audio_filename_with_extension = audio + '.wav'
    os.rename(audio, audio_filename_with_extension)
    
    audio_file = open(audio_filename_with_extension, "rb")
    client = openai.OpenAI()
    transcript = client.audio.transcriptions.create(
        model="whisper-1",file=audio_file
    )

    messages.append({"role": "user",
                     "content": transcript.text})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )

    system_message = response.choices[0].message
    messages.append(system_message)

    # calling the system voice with the text
    tts = gTTS(system_message.content, lang='nl')
    current_time = datetime.now()
    output_filename = "{}.mp3".format(current_time)
    tts.save(output_filename)
    playsound(output_filename)

    chat_transcript = system_message.role + \
                      ": " + system_message.content + \
                      "\n\n"

    return chat_transcript


ui = gr.Interface(fn=transcribe,
                  inputs=gr.Audio(sources=["microphone"], type="filepath"),
                  outputs="text")
ui.launch()
