import speech_recognition as sr
import boto3
import os
import asyncio
from ollama import AsyncClient

# Ініціалізація клієнта Amazon Polly
polly = boto3.client('polly', region_name='us-west-2')

async def ask_llama(messages):
    client = AsyncClient()
    response_stream = await client.chat(model="llama3.1:8b", messages=messages, stream=True)
    accumulated_text = ""
    async for part in response_stream:
        content = part["message"]["content"]
        accumulated_text += content

        if any(content.endswith(end) for end in [".", "!", "?"]):
            print(accumulated_text, end="", flush=True)
            await speak_response(accumulated_text)
            accumulated_text = ""

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Слухаю ваш запит...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio, language="uk-UA")
            print(f"Ви сказали: {query}")
            return query
        except sr.UnknownValueError:
            print("Не вдалося розпізнати голос.")
            return None
        except sr.RequestError:
            print("Помилка з'єднання зі службою розпізнавання.")
            return None

async def speak_response(response):
    ssml_text = f"""
    <speak>
        <prosody rate="medium" pitch="medium" volume="medium">
            {response}
        </prosody>
    </speak>
    """
    result = polly.synthesize_speech(
        TextType='ssml',
        Text=ssml_text,
        OutputFormat='mp3',
        VoiceId='Joanna'
    )
    with open('response.mp3', 'wb') as file:
        file.write(result['AudioStream'].read())
    os.system("mpg321 response.mp3 > /dev/null 2>&1")

async def main():
    messages = []  # Ініціалізуємо історію діалогу

    while True:
        question = recognize_speech()
        if question:
            messages.append({"role": "user", "content": question})
            await ask_llama(messages)

if __name__ == "__main__":
    asyncio.run(main())
