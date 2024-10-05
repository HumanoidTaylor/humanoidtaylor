import whisper
import os
import time

def main():
    input_folder = 'answer_me_that'
    output_folder = 'out_put_text'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load the Whisper model (options: tiny, base, small, medium, large)
    model = whisper.load_model("base")

    print("Monitoring folder for new WAV files. Press Ctrl+C to exit.")

    try:
        while True:
            # List all WAV files in the input folder
            wav_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.wav')]

            if wav_files:
                for wav_file in wav_files:
                    input_path = os.path.join(input_folder, wav_file)
                    print(f"Transcribing {wav_file}...")

                    try:
                        result = model.transcribe(input_path)
                        # Generate timestamp for the output filename
                        timestamp = time.strftime("%Y%m%d%H%M%S")
                        output_filename = f"{timestamp}.txt"
                        output_path = os.path.join(output_folder, output_filename)

                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(result["text"])

                        print(f"Transcription saved to {output_filename}")

                        # Delete the WAV file after successful transcription
                        os.remove(input_path)
                        print(f"Deleted {wav_file} from {input_folder}")

                    except Exception as e:
                        print(f"An error occurred while transcribing {wav_file}: {e}")
                        # Optionally, handle the error or move the file to an error directory

            # Wait for a short period before checking again
            time.sleep(10)  # Adjust the sleep time as needed

    except KeyboardInterrupt:
        print("\nScript terminated by user.")

if __name__ == "__main__":
    main()

