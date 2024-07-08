from dotenv import load_dotenv
load_dotenv()

from nicegui import ui

class MetapromptingSystem:
    def __init__(self):
        pass
    
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import HumanMessage


@ui.page('/')
def meta_prompting_page():
    
    with ui.grid(columns=3):
        ui.textarea(label='Prompt Skeleton',
            placeholder='Foobar'
        )
        ui.textarea(label='Prompt',
            placeholder='Foobar'
        )
        ui.space()
        ui.textarea(label='Refinement Prompt',
            placeholder='Foobar',
            value="""
            The assistant is an expert prompt engineer.
            The task is to produce a better prompt, based on the analysis of the input and output. Keep passing human approval criteria a high priority.
            """
        )
        ui.textarea(label='Output',
            placeholder='Foobar'
        )
        ui.space()
    ui.button('Refine', on_click=lambda: ui.notify('Refining'))
ui.run()


