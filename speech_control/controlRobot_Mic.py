import os
import random
import pygame
import serial
import threading
import time
from pydub import AudioSegment
import simpleaudio as sa
import wave
import signal

COMMENTS_WAV_DIR = "comments_wav/"
PRE_RECORDED_WAV_DIR = "pre-recorded/"
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

def signal_handler(sig, frame):
    print('Shutdown signal received. Cleaning up...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def get_wav_duration(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
    return duration

def move_jaw_to_sound(current_wav):
    last_angle = None  # Store the last angle to compare changes
    sound = AudioSegment.from_file(current_wav, format="wav")
    raw_data = sound.raw_data
    frame_rate = sound.frame_rate
    sample_width = sound.sample_width
    wav_duration = get_wav_duration(current_wav)
    print(wav_duration)
    play_obj = sa.play_buffer(raw_data, sound.channels, sample_width, frame_rate)
    print("Audio playback started")
    start_time = time.time()
    for chunk in sound[::50]:
        amplitude = max(chunk.get_array_of_samples())
        angle = map_amplitude_to_angle(amplitude, last_angle)
        last_angle = angle  # Update the last angle
        random_number = random.randint(1, 11)
        random_angle = random.randint(85, 95)
        send_command(str(random_number), str(random_angle))
        send_command("12", str(angle))
        elapsed_time = time.time() - start_time
        if elapsed_time >= wav_duration:
            break
        time.sleep(0.05)

def map_amplitude_to_angle(amplitude, last_angle=None):
    max_amplitude = 21000
    min_angle = 95
    max_angle = 110
    angle_range = max_angle - min_angle
    angle = ((amplitude / max_amplitude) * angle_range) + min_angle
    angle = int(angle)
    # Introduce a minimum movement threshold to ensure natural motion
    min_movement_threshold = 10  # Minimum angle change to simulate natural movement
    if last_angle is not None and abs(last_angle - angle) < min_movement_threshold:
        # Adjust the angle slightly to simulate mouth movement
        if angle + min_movement_threshold <= max_angle:
            angle += min_movement_threshold
        elif angle - min_movement_threshold >= min_angle:
            angle -= min_movement_threshold
    return angle

def send_command(gpio, angle):
    try:
        command = f"{gpio}|{angle}\n"
        ser.flushInput()
        ser.write(command.encode())
        response = ser.readline().decode().strip()
    except serial.SerialException as e:
        print("Serial Exception:", e)

def send_commandeyese(gpio, red, blue, green, bright):
    try:
        command = f"{gpio}|{red}|{blue}|{green}|{bright}\n"
        ser.write(command.encode())
        ser.flushInput()
        response = ser.readline().decode().strip()
        print(response)
    except serial.SerialException as e:
        print("Serial Exception:", e)

def play_and_delete_wav_files():
    while True:
        with open('eyeschange.txt', 'r') as file:
            content = file.read().strip()
        # Convert the content to an integer
        try:
            number = int(content)
        except ValueError:
            print("The file does not contain a valid integer.")
            number = None
        if number != 0:
            if number is not None:
                # Check if the number is between 1 and 5
                if number == 1:
                    print("Number is 1. Performing action for 1.")
                    send_commandeyese("13", "0", "128", "128", "255")
                    number = 0
                elif number == 2:
                    print("Number is 2. Performing action for 2.")
                    send_commandeyese("13", "64", "224", "208", "255")
                    number = 0
                elif number == 3:
                    print("Number is 3. Performing action for 3.")
                    send_commandeyese("13", "255", "255", "255", "255")
                    number = 0
                elif number == 4:
                    print("Number is 4. Performing action for 4.")
                    send_commandeyese("13", "255", "250", "205", "255")
                    number = 0
                elif number == 5:
                    print("Number is 5. Performing action for 5.")
                    number = 0
                else:
                    print("Number is not between 1 and 5 or invalid.")
                # Write the updated number back to the file
                if number is not None:
                    with open('eyeschange.txt', 'w') as file:
                        file.write(str(number))
        wav_files = [f for f in os.listdir(COMMENTS_WAV_DIR) if f.endswith(".wav")]
        if wav_files:
            for wav_file in wav_files:
                wav_path = os.path.join(COMMENTS_WAV_DIR, wav_file)
                move_jaw_to_sound(wav_path)
                os.remove(wav_path)  # Delete the WAV file after playing
        time.sleep(1)  # Adjust the sleep interval as needed

def main():
    pygame.init()
    print("Starting TikTok Live event listener...")
    print("pausing for 20sec")
    print("pausing done for 20sec")
    threading.Thread(target=play_and_delete_wav_files).start()

if __name__ == "__main__":
    main()

