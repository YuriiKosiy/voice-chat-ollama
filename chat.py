import speech_recognition as sr
import boto3
import os
from ollama import Client

# Ініціалізація клієнта Amazon Polly
polly = boto3.client('polly', region_name='us-west-2')

def ask_llama(messages):
    """
    Надсилає текстовий запит до моделі Llama3.1:8b і повертає відповідь.
    """
    client = Client()
    response = client.chat(
        model="llama3.1:8b", messages=messages
    )
    return response['message']['content']

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

def speak_response(response):
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
    os.system("mpg321 response.mp3")

def main():
    messages = []  # Ініціалізуємо історію діалогу

    while True:
        question = recognize_speech()
        if question:
            messages.append({"role": "user", "content": question})
            response = ask_llama(messages)
            print(f"Відповідь: {response}")
            messages.append({"role": "assistant", "content": response})
            speak_response(response)

if __name__ == "__main__":
    main()
