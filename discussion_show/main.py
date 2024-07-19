from nicegui import ui, run
from nicegui.element import Element

import runpod
import tempfile
import time

from dotenv import load_dotenv
load_dotenv()

from typing import Callable, Optional

from openai import OpenAI

# Taken from https://github.com/CVxTz/LLM-Voice/blob/master/llm_voice/audio_recorder.py
class AudioRecorder(Element, component="audio_recorder.vue"):
    def __init__(self, *, on_audio_ready: Optional[Callable] = None) -> None:
        super().__init__()
        self.on("audio_ready", on_audio_ready)

    async def start_recording(self) -> None:
        self.run_method("startRecording")

    async def stop_recording(self) -> None:
        self.run_method("stopRecording")

    async def play_recorded_audio(self) -> None:
        self.run_method("playRecordedAudio")

class AudioTranscriber:
    def __init__(self):
        self.whisper = None
        self.openai = OpenAI()

    async def transcribe(self, audio_blob):
        # Check size < 25 MB
        # Check filetype
        pass

class MyContextBuffer:
    def __init__(self):
        self.context = ""
        self.full_enough = 250

    def add_to_context(self, text):
        self.context += text

    def is_full_enough(self):
        if len(self.context) > self.full_enough:
            return True
        else:
            return False

class ImageGenerator:
    def __init__(self):
        pass

@ui.page("/")
async def main():
    ui.label("Hello World")
    transcriber = AudioTranscriber()
    my_context_buffer = MyContextBuffer()
    image_generator = ImageGenerator(context=my_context_buffer)

    listener = AudioRecorder(on_audio_ready=lambda audio: my_context_buffer.add_to_context(transcriber.transcribe(audio)))

ui.run(port=8080)

# This class listens to the microphone
# and makes SoundBite objects
# which are then processed and added
# to the context
# import asyncio
# class AudioListener:
#     def __init__(self, start_recording, stop_recording, seconds_to_listen=15):
#         self.start_recording = start_recording 
#         self.stop_recording = stop_recording
#         self.seconds_to_listen = seconds_to_listen
#         pass
# 
#     async def record(self):
#         sound_bite = SoundBite()
#         print(f"Path to sound bite: {sound_bite.file.name}")
#         await self.start_recording(sound_bite.file.name)
#         await asyncio.sleep(self.seconds_to_listen)
#         await self.stop_recording()
#         return sound_bite
# 
#     async def get_contexts(self):
#         context = MyContext()
#         while context.is_full_enough() == False:
#             sound_bite = await self.record()
#             context.text += sound_bite.to_text()
#         yield context
# 
#     
# # Inspiration from https://gist.github.com/arctic-hen7/5580d5452f77d4e6b206caf90f8d73c6
# 
# # This class represents a sound clip
# # in a temp file
# class SoundBite:
#     def __init__(self):
#         self.file = tempfile.NamedTemporaryFile(suffix=".wav")
# 
#     def to_text(self):
#         # Use the whisper API
#         return ""
#     
# 
# # This represents a context that
# # the chat agent can use to generate
# # the image
# class MyContext:
#     def __init__(self):
#         self.text = ""
#         self.full_enough = 250
#         pass
# 
#     def is_full_enough(self):
#         if len(self.text) > self.full_enough:
#             return True
#         else:
#             return False
# 
# # This class generates images from
# # a context
# class ImageGenerator:
#     def __init__(self):
#         pass
# 
#     def generate_image_from_context(self, context):
#         generated_image = GeneratedImage()
#         return generated_image
#         # Use langchain to turn the context
#         # into a suitable prompt for an image
#         # generator
# 
#         # Then use the image generator API via runpod
#         # to generate an image, and put the data
#         # into a GeneratedImage object
# 
# # This represents a generated image
# # that can be displayed in
# # base64 format
# class GeneratedImage:
#     def __init__(self):
#         self.base64 = ""
#         self.file_type = "png"
#         pass
#     
# 
# async def main(page: ft.Page):
#     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
#     display = ft.ListView(auto_scroll=True, expand=True)
#     # Add a button to enable or disable audio listening
#     # as a toggle with an icon for mute/unmute
# 
#     # Show a meter that displays the amount of context
#     # that has been generated so far
# 
#     # The objective is to continuously listen to the microphone
#     # and use the openai whisper API to convert speech to text
#     # and then use the text to generate an image
# 
#     audio_rec = ft.AudioRecorder(
#         audio_encoder=ft.AudioEncoder.WAV,
#     )
#     page.add(audio_rec)
# 
#     async def start_recording(file_path):
#         audio_rec.start_recording(file_path)
# 
#     async def stop_recording():
#         audio_rec.stop_recording()
# 
#     seconds_to_listen = 5
#     listener = AudioListener(start_recording=start_recording, stop_recording=stop_recording, seconds_to_listen=seconds_to_listen)
#     image_generator = ImageGenerator()
# 
#     async for context in listener.get_contexts():
#         print(f"Context: {context.text}")
#         generated_image = image_generator.generate_image_from_context(context)
#         # display image here
# 
#     # while True:
#     #     while context.is_full_enough() == False:
#     #         sound_bite = listener.record()
#     #         context.text += sound_bite.to_text()
#     #     generated_image = image_generator.generate_image_from_context(context)
# 
#     page.add(
#         display
#     )
# 
#     page.update()
# 
# ft.app(target=main)