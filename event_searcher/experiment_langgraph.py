from nicegui import ui
import os
from dotenv import load_dotenv
import agentops

load_dotenv()

# Initialize AgentOps
agentops.init(os.environ.get('AGENTOPS_API_KEY'))

# Singleton class for configuration
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.openai_api_key = os.environ.get('OPENAI_API_KEY')
            cls._instance.openai_api_url = "https://api.openai.com/v1/"
            cls._instance.openai_model_name = os.environ.get('OPENAI_MODEL_NAME', 'gpt-4o')
        return cls._instance

from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

class State(TypedDict):
    messages: Annotated[list, add_messages]

from langchain_openai import ChatOpenAI

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import Tool
from langgraph.prebuilt import ToolNode

class Nexus:
    def __init__(self, config: Config):
        self.config = config

        serper = self.setup_serper()
        self.tools = [
            serper
        ]

        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            base_url=self.config.openai_api_url,
            model=self.config.openai_model_name
        ).bind_tools(self.tools)

        tool_node = ToolNode(self.tools)

        graph_builder = StateGraph(State)

        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_node("action", tool_node)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges(
            "chatbot",
            self.should_continue,
        )
        graph_builder.add_edge("action", "chatbot")
        graph_builder.add_edge("chatbot", END)

        memory = AsyncSqliteSaver.from_conn_string(":memory:")
        self.graph = graph_builder.compile(checkpointer=memory)

    @agentops.record_function('setup_serper')
    def setup_serper():
        search = GoogleSerperAPIWrapper()
        print("setup_serper")
        return Tool(
            name="Google Search",
            func=search.run,
            description="Google search API, useful for finding relevant sites on the internet"
        )

    @agentops.record_function('should_continue')
    def should_continue(state: State) -> Literal["action", "__end__"]:
        """Return the next node to execute."""
        last_message = state["messages"][-1]
        print("Inside should_continue")
        # If there is no function call, then we finish
        if not last_message.tool_calls:
            return "__end__"
        # Otherwise if there is, we continue
        return "action"

    @agentops.record_function('chatbot')
    def chatbot(self, state: State):
        print("Inside chatbot")
        return {"messages": [self.llm.invoke(state["messages"])]}
    
    @agentops.record_function('chat')
    async def chat(self, thread_id, message):
        response = ''
        spin = ui.spinner()
        print("Chatting with agent...")
        async for event in self.graph.astream({"messages": [message]},
            {"configurable": {"thread_id": thread_id}}):
            for value in event.values():
                for message in value["messages"]:
                    response += message.content + '\n'
                    ui.markdown(f"{response}")
        spin.delete()

@ui.page('/')
def main():
    config = Config()
    nexus = Nexus(config)
    
    # The purpose of this application is to find events that
    # the user might like to go to. The user can input their
    # preferences by chatting with the agent directly.

    @agentops.record_function('send')
    async def send() -> None:
        question = text.value
        text.value = ''

        print("Sending question to agent...")

        with message_container:
            ui.chat_message(text=question, name='You', sent=True)
            response_message = ui.chat_message(name=config.openai_model_name, sent=False)

        response = ''
        with response_message:
            await nexus.chat("pat", question)
            response_message.sent = True

        ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

    ui.page_title('Langgraph Example Chat')

    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('Chat')
        settings_tab = ui.tab('Settings')
    
    with ui.tab_panels(tabs, value=chat_tab).classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        with ui.tab_panel(chat_tab).classes('items-stretch'):
            message_container = ui.column().classes('w-full')
            with ui.column().classes('w-full'):
                placeholder = 'message'
                text = ui.input(placeholder=placeholder).props('rounded outlined input-class=max-3').classes('w-full self-center').on('keydown.enter', send)

        with ui.tab_panel(settings_tab).classes('items-stretch'):
            ui.label('Settings')
            ui.input(label="OPENAI_API_URL", placeholder=config.openai_api_url, on_change=lambda e: setattr(config, 'openai_api_url', e.value))
            ui.input(label="OPENAI_API_KEY", password=True, on_change=lambda e: setattr(config, 'openai_api_key', e.value))
            ui.input(label="OPENAI_MODEL_NAME", placeholder=config.openai_model_name, on_change=lambda e: setattr(config, 'openai_model_name', e.value))

    # The agent will ask the user for their preferences and
    # then find events that match those preferences.

if __name__ == "__main__":
    try:
        ui.run()
    finally:
        agentops.end_session('Success')