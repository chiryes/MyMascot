import requests
import json
import io
import wave
import pyaudio
import time

class Speak:
    def __init__(self, host="127.0.0.1", port=50021):
        self.host = host
        self.port = port
    def speak(self, text=None, speaker=48):
        params = (
            ("text", text),
            ("speaker", speaker)
        )
        init_q = requests.post(
            f"http://{self.host}:{self.port}/audio_query",
            params=params
        )
        res = requests.post(
            f"http://{self.host}:{self.port}/synthesis",
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(init_q.json())
        )
        audio = io.BytesIO(res.content)
        with wave.open(audio,'rb') as f:
            p = pyaudio.PyAudio()
            def _callback(in_data, frame_count, time_info, status):
                data = f.readframes(frame_count)
                return (data, pyaudio.paContinue)
            stream = p.open(format=p.get_format_from_width(width=f.getsampwidth()), channels=f.getnchannels(), rate=f.getframerate(), output=True, stream_callback=_callback)
            stream.start_stream()
            while stream.is_active():
                time.sleep(0.1)

            stream.stop_stream()
            stream.close()
            p.terminate()
