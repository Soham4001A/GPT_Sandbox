from openai import OpenAI

client = OpenAI(api_key='API_KEY')
import speech_recognition as sr
from gtts import gTTS
import pygame
import os

# Initialize pygame mixer for audio playback
pygame.mixer.init()

def speak(text):
    """ Function to speak the provided text using gTTS """
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")

    # Load and play the saved audio file
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Adjust tick rate if needed

def listen():
    """ Function to listen for user voice input """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        user_input = recognizer.recognize_google(audio)
        print(f"You: {user_input}")
        return user_input.lower()
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""

def start_conversation():
    print("Welcome to the GPT-4 Omni conversation demo.")

    while True:
        user_input = listen()

        if user_input == 'end':
            print("Ending conversation...")
            break

        try:
            # Create a chat completion using user input
            response = client.chat.completions.create(model="gpt-4o",
            messages=[
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=150)

            # Extract the response text from the API response correctly
            if response.choices and len(response.choices) > 0:
                gpt_response = response.choices[0].message.content.strip()
                print(f"GPT-4 Omni: {gpt_response}")

                # Speak the response using gTTS
                speak(gpt_response)

                # Wait until the response is fully spoken before listening again
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_conversation()
