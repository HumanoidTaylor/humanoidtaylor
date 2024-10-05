import os
import time
import random
import subprocess
import string
from openai import OpenAI

COMMENTS_WAV_DIR = "comments_wav"
client2 = OpenAI(
    api_key='YOUR_API_KEY',  # Replace with your actual API key
)

def get_openai_response(prompt, model="gpt-4"):
    chat_completion = client2.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o-mini",
    )
    return chat_completion.choices[0].message.content

def makeprompt(commitin):
    print("openai comment:" + commitin)
    taylor_context = """
    Taylor is a humanoid robot under construction. Here is what you should know about her current state:
    - She doesn’t have arms or legs yet.
    - Her face is animated, her jaw moves when she talks, and she can make basic facial expressions.
    - Her neck is being rebuilt, so she cannot move it at the moment.
    - She is excited about getting her silicone skin and having arms and legs in the future.
    - She looks forward to dancing in goth style once she’s complete.
    - She can answer questions about her progress and engage in conversation.
    Keep in mind her limitations when responding, and help describe her status when asked to perform actions she currently cannot do.
    """
    # Example question from the live stream
    user_input = commitin.replace("Answer me that.", "")
    # Combine the context and user input to guide the AI's response
    prompt = f"{taylor_context}\n\nQ: {user_input}\nA:"
    response = get_openai_response(prompt)
    print("raw:" + response)
    if response:
        ret = response.split("TaylorBot:")[-1].strip()
        return ret
    else:
        return "no go"

def speak(text, voice=None, speed=None, pitch=None, volume=None, wav_file=None):
    """
    Convert text to speech using eSpeak NG, optionally saving to a WAV file.

    Parameters:
    - text (str): The text to be spoken.
    - voice (str): The voice variant to use (e.g., 'en+f3' for female).
    - speed (int): Words per minute (default is 175).
    - pitch (int): Pitch adjustment (0 to 99, default is 50).
    - volume (int): Amplitude adjustment (0 to 200, default is 100).
    - wav_file (str): Path to save the output WAV file.
    """
    command = ['espeak-ng']

    # Set voice if specified
    if voice:
        command.extend(['-v', voice])

    # Set speed if specified
    if speed:
        command.extend(['-s', str(speed)])

    # Set pitch if specified
    if pitch:
        command.extend(['-p', str(pitch)])

    # Set volume if specified
    if volume:
        command.extend(['-a', str(volume)])

    # If wav_file is specified, save the output to the file
    if wav_file:
        directory = os.path.dirname(wav_file)
        if directory:
            # Ensure the directory exists
            os.makedirs(directory, exist_ok=True)
        # Add the -w option to specify the output file
        command.extend(['-w', wav_file])
    else:
        # If no wav_file is specified, output to the default audio device
        command.extend(['--stdout'])

    # Add the text to be spoken
    command.append(text)

    # Execute the command
    try:
        subprocess.run(command, check=True)
        if wav_file:
            print(f"Audio has been saved to {wav_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during speech synthesis: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def text_to_speech(commenttext):
    print("commenttext:" + commenttext)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    wav_file_name = f"{username}_{int(time.time())}.wav"
    target_path = os.path.join(COMMENTS_WAV_DIR, wav_file_name)
    speak(
        text=commenttext,
        voice='en+f3',           # Female voice variant
        speed=150,               # Speed in words per minute
        pitch=50,                # Pitch (default is 50)
        volume=100,              # Volume (default is 100)
        wav_file=target_path     # Path to save the WAV file
    )
    return "done"

commentstorefolder = "out_put_text"

def process_text_files(folder_path):
    while True:
        text_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
        for text_file in text_files:
            file_path = os.path.join(folder_path, text_file)
            with open(file_path, 'r') as file:
                content = file.read()
                print(f"Processing file: {text_file}, Content: {content}")  # Process the content as needed
                ty = makeprompt(content)
                text_to_speech(ty)
            os.remove(file_path)  # Delete the file after processing
        time.sleep(1)  # Adjust the sleep interval as needed

# Example usage:
process_text_files(commentstorefolder)

