import flet as ft

from custom.gen_ai import FletAIInterface

from dotenv import load_dotenv

load_dotenv()

# The app is going to be a showcase of
# talking to a chat agent that has the
# ability to generate Flet controls
# on demand, with lots of options to keep
# it interesting.

# Image generation API will be a welcome addition.

def main(page: ft.Page):
    chat = ft.ListView(auto_scroll=True, expand=True)
    new_message = ft.TextField(value="hello, sample multiple text field sizes with lorem ipsum. call the text tool multiple times for different sizes")
    flai = FletAIInterface()

    def send_click(e):
        sent_value = new_message.value
        chat.controls.append(ft.Row(
            controls=[ft.Text(new_message.value)]
        ))
        new_message.value = ""
        page.update()

        flai.respond(page, chat, sent_value)
        page.update()

    page.add(
        chat, ft.Row(controls=[new_message, ft.ElevatedButton("Send", on_click=send_click)])
    )

ft.app(target=main)