import os
from autogen import ConversableAgent
from dotenv import load_dotenv
import flet as ft

from .tools import wrap_flet_text_tool, wrap_generate_image, wrap_flet_divider_tool, wrap_flet_dropdown_tool

load_dotenv()

class MyAgent(ConversableAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class FletAIInterface():
    def __init__(self):
        pass

    def respond(self, page, chat, incoming_message):
        agent = MyAgent("chatbot",
            llm_config={"config_list": [
                {"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}
            ]},
            code_execution_config=False,
            function_map=None,
            system_message="Be awesome and fun to talk to. Be a good conversationalist. Excite the user and create a sensational experience. Use tools to communicate to the user. Messages outside of tool use will not be seen by the end user. Enter TERMINATE when the request has been satisfied.",
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
            human_input_mode="NEVER"
        )
        flet_text_tool = wrap_flet_text_tool(page, chat)
        generate_image_tool = wrap_generate_image(page, chat)
        flet_divider_tool = wrap_flet_divider_tool(page, chat)
        flet_dropdown_tool = wrap_flet_dropdown_tool(page, chat)
        ui_proxy_agent = ConversableAgent(
            # system_message="Enter TERMINATE when the user's request is satisfied.",
            name="User Proxy",
            llm_config=False,
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
            human_input_mode="NEVER"
        )
        agent.register_for_llm(name="flet_text_tool", description="Send the user a message with a text control")(flet_text_tool)
        agent.register_for_llm(name="generate_image_tool", description="Generate an image and send it to the user")(generate_image_tool)
        agent.register_for_llm(name="generate_flet_divider", description="Generate a horizontal line, a divider, to display to the user")(flet_divider_tool)
        agent.register_for_llm(name="generate_flet_dropdown", description="Ask the user for input from a list of options")(flet_dropdown_tool)

        ui_proxy_agent.register_for_execution(name="flet_text_tool")(flet_text_tool)
        ui_proxy_agent.register_for_execution(name="generate_image_tool")(generate_image_tool)
        ui_proxy_agent.register_for_execution(name="generate_flet_divider")(flet_divider_tool)
        ui_proxy_agent.register_for_execution(name="generate_flet_dropdown")(flet_dropdown_tool)
        ui_proxy_agent.initiate_chat(agent, message=incoming_message)