import os
import threading
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from datetime import datetime
import re

def record_until_phrase(pattern, input_device_index, folder_name="answer_me_that"):
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Initialize variables
    fs = 44100  # Sample rate
    channels = 1  # Mono audio
    q = queue.Queue()
    recording = []
    recognizer = sr.Recognizer()

    def callback(indata, frames, time, status):
        if status:
            print(f"Status: {status}", flush=True)
        q.put(indata.copy())
        print(f"Callback received {frames} frames", flush=True)

    def process_audio():
        buffer = []
        buffer_duration = 3  # Duration in seconds for each recognition attempt
        samples_per_buffer = int(fs * buffer_duration)
        while not stop_event.is_set():
            if not q.empty():
                data = q.get()
                recording.append(data)
                buffer.append(data)
                current_buffer_length = sum([len(chunk) for chunk in buffer])
                print(f"Buffer length: {current_buffer_length} samples", flush=True)
                if current_buffer_length >= samples_per_buffer:
                    # Concatenate buffered data
                    buffered_data = np.concatenate(buffer, axis=0)
                    # Reset buffer
                    buffer = []
                    # Convert audio data to the format expected by speech_recognition
                    audio_data = np.int16(buffered_data * 32767).tobytes()
                    audio = sr.AudioData(audio_data, fs, 2)
                    try:
                        text = recognizer.recognize_google(audio)
                        print(f"You said: {text}", flush=True)
                        # Use regular expression matching
                        if re.search(pattern, text, re.IGNORECASE):
                            print("Stop phrase detected. Stopping recording.", flush=True)
                            stop_event.set()
                    except sr.UnknownValueError:
                        print("Could not understand audio.", flush=True)
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}", flush=True)
                    except Exception as e:
                        print(f"An unexpected error occurred during recognition: {e}", flush=True)
            else:
                sd.sleep(100)  # Sleep to prevent high CPU usage

    stop_event = threading.Event()

    # Start processing thread
    processing_thread = threading.Thread(target=process_audio)
    processing_thread.start()

    # Start recording
    print("Recording started. Say the stop phrase to stop recording.", flush=True)
    try:
        with sd.InputStream(samplerate=fs, channels=channels, callback=callback, device=input_device_index):
            while not stop_event.is_set():
                sd.sleep(100)
    except Exception as e:
        print(f"Error with InputStream: {e}", flush=True)
        stop_event.set()

    # Wait for processing thread to finish
    processing_thread.join()

    # Concatenate all recorded data
    if recording:
        recording = np.concatenate(recording, axis=0)

        # Generate a filename with timestamp
        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.wav")
        filepath = os.path.join(folder_name, filename)

        # Save the recording
        try:
            sf.write(filepath, recording, fs)
            print(f"Recording saved to {filepath}", flush=True)
        except Exception as e:
            print(f"Error saving recording: {e}", flush=True)
    else:
        print("No audio was recorded.", flush=True)

def main():
    with open('eyeschange.txt', 'w') as file:
        file.write('0')
    recognizer = sr.Recognizer()

    # List available microphones and select the correct one
    print("Available microphone devices:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{index}: {name}")

    # Set your microphone index here
    mic_index = int(input("Enter the device index of your microphone: "))
    mic = sr.Microphone(device_index=mic_index)

    # List sounddevice input devices
    print("\nAvailable sounddevice input devices:")
    for idx, device in enumerate(sd.query_devices()):
        if device['max_input_channels'] > 0:
            print(f"{idx}: {device['name']}")
    input_device_index = int(input("Enter the sounddevice input device index for your microphone: "))

    print("Adjusting for ambient noise, please wait...", flush=True)
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
    print("Listening...", flush=True)

    while True:
        try:
            with mic as source:
                print("Please speak your command:", flush=True)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            try:
                text = recognizer.recognize_google(audio)
                print(f"Recognized text: {text}", flush=True)

                if re.search(r'taylor', text, re.IGNORECASE):
                    print("Starting recording...", flush=True)
                    with open('eyeschange.txt', 'w') as file:
                        file.write('1')
                    # Use a regular expression pattern for 'think' with wildcards
                    pattern = r'.*think.*'  # Adjust the pattern as needed
                    record_until_phrase(pattern, input_device_index)
                    with open('eyeschange.txt', 'w') as file:
                        file.write('2')
                    print("Recording finished. Resuming listening...", flush=True)
                elif text.lower() == "combat mode":
                    with open('eyeschange.txt', 'w') as file:
                        file.write('3')
                    print("Combat mode activated.", flush=True)
                    # Implement combat mode functionality here
                else:
                    print("Command not recognized.", flush=True)

            except sr.UnknownValueError:
                print("Speech Recognition could not understand the audio.", flush=True)
            except sr.RequestError as e:
                print(f"Could not request results; {e}", flush=True)
            except Exception as e:
                print(f"An unexpected error occurred: {e}", flush=True)

        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.", flush=True)
        except KeyboardInterrupt:
            print("Program terminated by user.", flush=True)
            break

if __name__ == "__main__":
    main()

