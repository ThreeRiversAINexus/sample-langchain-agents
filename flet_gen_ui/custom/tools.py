from typing import Annotated, Literal
import flet as ft

import os
from dotenv import load_dotenv

import requests
import json
import base64

load_dotenv

class RunPodAPI:
    def __init__(self, api_key, base_url="https://api.runpod.ai/v2"):
        self.api_key = api_key
        self.base_url = base_url

    def start_job(self, endpoint_id, prompt):
        url = f"{self.base_url}/{endpoint_id}/runsync"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        data = {
            "input": {
                "prompt": prompt
            }
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def check_status(self, endpoint_id, job_status_id):
        url = f"{self.base_url}/{endpoint_id}/status/{job_status_id}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def decode_image(self, json_data):
        try:
            base64_image = json_data["output"]["image_url"]
            base64_image = base64_image.replace("data:image/png;base64,", "")
            return base64_image
        except KeyError as e:
            print(f"Error in JSON structure: {e}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_results(self, endpoint_id, job_status_id):
        json_data = self.check_status(endpoint_id, job_status_id)
        while json_data.get("status") != "COMPLETED":
            print("Waiting...")
            json_data = self.check_status(endpoint_id, job_status_id)
        return self.decode_image(json_data)

def wrap_flet_dropdown_tool(page, chat):
    def flet_dropdown_tool(options: Annotated[str, "A CSV list of options to put in a dropdown UI control"]) -> Annotated[str, "Success = Successfully added dropdown UI"]:
        chat.controls.append(ft.Row(
            controls=[
                ft.Dropdown(
                    width=100,
                    options=[ft.dropdown.Option(x) for x in options.split(",")]
                )
            ],
            expand=True
        ))
        page.update()
        return "Success"
    return flet_dropdown_tool

def wrap_flet_divider_tool(page, chat):
    def flet_divider_tool() -> Annotated[str, "Success = Successfully added a thin horizontal divider"]:
        chat.controls.append(
                ft.Divider()
        )
        page.update()
        return "Success"
    return flet_divider_tool

def wrap_flet_text_tool(page, chat):
    def flet_text_tool(content: Annotated[str, "This is a message visible to the user in the text control"], size: Annotated[int, "Represents the size of the element 0 to 100, 20 is normal"], bgcolor: Annotated[str, "Hex RGB value for the background color"], color: Annotated[str, "Hex RGB value for the text color"]) -> Annotated[str, "Success = Successfully generated text field"]:
        chat.controls.append(ft.Text(content, size=size, color=color, bgcolor=bgcolor))
        page.update()
        return "Success"

    return flet_text_tool

def wrap_generate_image(page, chat):
    def generate_image_tool(prompt: Annotated[str, "This is a description of the image to be generated"]) -> Annotated[str, "Success = Successfully generated and displayed the image"]:
        # Interact with stable diffusion API
        # Extract the image and add it here
        # Update the page

        # Example usage:
        api_key = os.environ.get("RUNPOD_API_KEY")
        endpoint_id = os.environ.get("RUNPOD_ENDPOINT")

        runpod_api = RunPodAPI(api_key)
        start_response = runpod_api.start_job(endpoint_id, prompt)
        job_status_id = start_response.get("id")

        # Checking the job status and retrieving the base64 content
        if job_status_id:
            base64_image = runpod_api.get_results(endpoint_id, job_status_id)
            if base64_image:
                print("Successfully extracted base64 image")
                chat.controls.append(ft.Image(src_base64=base64_image, fit=ft.ImageFit.SCALE_DOWN, height=512, width=512))
                page.update()
        else:
            print("Failed to start the job.")
        return "Success"
    
    return generate_image_tool