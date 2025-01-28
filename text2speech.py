import os
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
        """Generates an output filename with an .mp3 extension based on the input file's basename."""
        base_name = os.path.splitext(os.path.basename(input_filename))[0]
        return f"{base_name}.wav"

    def text_to_speech(self, text: str, speed_factor=0.9) -> str:
        """Converts text to speech, slows it down, and saves the output to a file."""
        try:
            chunk_size = 1999
            chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
            combined_audio = AudioSegment.silent(duration=0)

            for chunk in chunks:
                temp_output_filename = "temp_chunk.wav"
                speak_params = {"text": chunk}

                self.client.speak.rest.v("1").save(temp_output_filename, speak_params, self.speak_options)

                chunk_audio = AudioSegment.from_wav(temp_output_filename)

                slowed_audio = chunk_audio._spawn(chunk_audio.raw_data, overrides={
                    "frame_rate": int(chunk_audio.frame_rate * speed_factor)
                }).set_frame_rate(chunk_audio.frame_rate)

                combined_audio += slowed_audio
                os.remove(temp_output_filename)

            combined_audio.export(self.output_filename, format="wav")
            print(f"Combined audio saved to {self.output_filename}")

            return self.output_filename
        except Exception as e:
            print(f"Error in text_to_speech: {e}")
            return ""

    def play_audio(self, filename: str):
        """Plays a WAV or MP3 audio file."""
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
