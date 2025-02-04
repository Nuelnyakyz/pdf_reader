import os
import time
from dotenv import load_dotenv
import simpleaudio as sa
from pydub import AudioSegment
from deepgram import DeepgramClient, SpeakOptions

load_dotenv()

class DeepgramTextToSpeech:
    def __init__(self, api_key: str, input_filename: str):
        self.api_key = api_key
        self.output_filename = self._generate_output_filename(input_filename)
        self.client = DeepgramClient(api_key)
        self.speak_options = SpeakOptions(
            model="aura-orpheus-en",
            encoding="linear16",
            container="wav" 
        )

    def _generate_output_filename(self, input_filename: str) -> str:
        base_name = os.path.splitext(os.path.basename(input_filename))[0]
        return f"{base_name}.wav"

    def text_to_speech(self, text: str, speed_factor=0.9, retries=3, delay=2) -> str:
        chunk_size = 1990
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        combined_audio = AudioSegment.silent(duration=0)

        print(f"No of chunks: {len(chunks)}")

        for index, chunk in enumerate(chunks):
            attempt = 0
            while attempt < retries:
                try:
                    temp_output_filename = "temp_chunk.wav"
                    speak_params = {"text": chunk}

                    self.client.speak.rest.v("1").save(temp_output_filename, speak_params, self.speak_options)

                    chunk_audio = AudioSegment.from_wav(temp_output_filename)

                    slowed_audio = chunk_audio._spawn(chunk_audio.raw_data, overrides={
                        "frame_rate": int(chunk_audio.frame_rate * speed_factor)
                    }).set_frame_rate(chunk_audio.frame_rate)

                    combined_audio += slowed_audio
                    os.remove(temp_output_filename)

                    print(f"Completed chunk {index + 1}/{len(chunks)}")
                    break 

                except Exception as e:
                    attempt += 1
                    print(f"Chunk {index + 1} failed, attempt {attempt}/{retries}: {e}")

                    if attempt < retries:
                        time.sleep(delay)
                    else:
                        print(f"Error: Unable to process chunk {index + 1} after {retries} retries. Stopping")
                        print("Unstable network connection. Please check your internet connection.")
                        return None  

        output_path = self.output_filename
        combined_audio.export(output_path, format="wav")
        print(f"Combined audio saved to {output_path}")

        return output_path

    def play_audio(self, filename: str):
        try:
            wave_obj = sa.WaveObject.from_wave_file(filename)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            play_obj.stop()
        except Exception as e:
            print(f"Error in play_audio: {e}")


def main():
    My_Deepgram_key = os.getenv('MY_DEEPGRAM_KEY')

    if not My_Deepgram_key:
        print("Deepgram API key not found in environment variables.")
        return

    pdf_file = "example.pdf"
    tts = DeepgramTextToSpeech(api_key=My_Deepgram_key, input_filename=pdf_file)

    output_file = tts.text_to_speech("Hi, Hello! I'm here! How can I assist you today?")
    if output_file:
        print('Playing audio...')
        tts.play_audio(output_file)
    else:
        print("Audio generation failed.")

if __name__ == "__main__":
    main()
