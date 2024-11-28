import openai
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import base64
import requests

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

def encode_image(image_path):
    """ Function to encode an image to base64 """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_images(image_folder):
    image_features = []
    for filename in os.listdir(image_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(image_folder, filename)
            base64_image = encode_image(image_path)
            image_features.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })
    return image_features

def start_conversation(api_key):
    print("Welcome to the GPT-4 Omni conversation demo.")

    while True:
        user_input = listen()
        #For testing
        #user_input = "What breed is this puppy?"

        if user_input == 'end':
            print("Ending conversation...")
            break

        try:
            # Get base64 encoded images from the specified folder
            image_folder = "/Users/sohamsane/Documents/Coding Projects/GPT_Vision/Images_Seen"
            image_features = process_images(image_folder)

            # Create the payload
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": user_input}, *image_features]
                    }
                ],
                "max_tokens": 300
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            # Send the request to the OpenAI API
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            # Extract the response text from the API response
            if response.status_code == 200:
                response_data = response.json()
                if response_data['choices'] and len(response_data['choices']) > 0:
                    gpt_response = response_data['choices'][0]['message']['content'].strip()
                    print(f"GPT-4 Omni: {gpt_response}")

                    # Speak the response using gTTS
                    speak(gpt_response)

                    # Wait until the response is fully spoken before listening again
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                else:
                    print("No response from GPT-4 Omni.")
            else:
                print(f"Error: {response.status_code}, {response.text}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Initialize OpenAI client with API key
    api_key = 'API_KEY'
    start_conversation(api_key)
