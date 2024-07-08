from nicegui import ui

import os
from dotenv import load_dotenv
load_dotenv()

# Singleton class for configuration
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.openai_api_key = os.environ.get('OPENAI_API_KEY')
            cls._instance.openai_api_url = "https://api.openai.com/v1/"
            cls._instance.openai_model_name = os.environ.get('OPENAI_MODEL_NAME', 'gpt-4o')
            cls._instance.system_message = ""
        return cls._instance

from typing import TYPE_CHECKING, Annotated, Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import Tool
from langgraph.prebuilt import ToolNode

from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

from langchain_core.messages import AIMessage
from langchain_core.messages import ToolMessage

from langchain_community.agent_toolkits import PlayWrightBrowserToolkit

from langchain_community.tools.playwright.utils import (
    create_async_playwright_browser,
)

from langchain_community.tools.playwright.navigate import NavigateTool

import nest_asyncio

class State(TypedDict):
    messages: Annotated[list, add_messages]

from langchain_openai import ChatOpenAI 

from my_utils.navigate import NexusNavigateTool

class Nexus:
    def __init__(self, config: Config):
        self.config = config

        self.tools = []
        self.tools += self.setup_playwright()
        self.tools += [self.setup_serper()]

        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            base_url=self.config.openai_api_url,
            model=self.config.openai_model_name
        ).bind_tools(self.tools)

        tool_node = ToolNode(self.tools)

        graph_builder = StateGraph(State)

        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_node("action", tool_node)
        # graph_builder.add_node("reflection", self.reflection)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges(
            "chatbot",
            self.should_continue,
        )
        # graph_builder.add_conditional_edge("chatbot", self.should_reflect)
        graph_builder.add_edge("action", "chatbot")
        # graph_builder.add_edge("reflection", "chatbot")
        # graph_builder.add_edge("reflection", END)
        # todo add reflection in langgraph with custom prompt
        # I don't think this is right, but it is a work in progress
        graph_builder.add_edge("chatbot", END)

        memory = AsyncSqliteSaver.from_conn_string(":memory:")
        self.graph = graph_builder.compile(checkpointer=memory)

    def setup_serper(self):
        search = GoogleSerperAPIWrapper()
        print("setup_serper")
        return Tool(
            name="google_search",
            func=search.run,
            description="Google search API, useful for finding relevant sites on the internet"
        )

    async def chatbot(self, state: State):
        print("Inside chatbot")

        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.messages import SystemMessage
        from langchain_core.prompts import HumanMessagePromptTemplate

        my_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=self.config.system_message
                ),
                HumanMessagePromptTemplate.from_template("""
                    {messages}
                """)
            ]
        )

        chain = my_prompt | self.llm

        # return {"messages": [self.llm.invoke(state["messages"])]}
        print(state["messages"])
        return {"messages": [await chain.ainvoke(state["messages"])]}

    def setup_playwright(self):
        # use create_async_playwright_browser
        # to create a browser instance
        nest_asyncio.apply()
        async_browser = create_async_playwright_browser()
        # create a new instance of the NexusNavigateTool
        # and pass the browser instance to it
        navigate = NexusNavigateTool.from_browser(async_browser=async_browser)

        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
        tools = toolkit.get_tools()

        # Filter out tool with object type NavigateTool
        tools = [tool for tool in tools if not isinstance(tool, NavigateTool)]
        tools.append(navigate)

        return tools

    def should_continue(self, state: State) -> Literal["action", "__end__"]:
        """Return the next node to execute."""
        last_message = state["messages"][-1]
        print("Inside should_continue")
        # If there is no function call, then we finish
        if not last_message.tool_calls:
            return "__end__"
        # Otherwise if there is, we continue
        return "action"
    
    async def chat(self, thread_id, message):
        response = ''
        print("Chatting with agent...")
        async for event in self.graph.astream({"messages": [message]},
            {"configurable": {"thread_id": thread_id}}):
            print("New event")
            for value in event.values():
                print("Value: ", value)
                for message in value["messages"]:
                    # If the message is an AIMessage, we want to display it
                    if isinstance(message, AIMessage):
                        response += message.content + '\n'
                        # ui.markdown(f"{response}")
                    # If the message is a ToolMessage, we want to log it
                    if isinstance(message, ToolMessage):
                        print(message)
        return response

@ui.page('/')
def main():
    config = Config()
    nexus = Nexus(config)
    
    # The purpose of this application is to find events that
    # the user might like to go to. The user can input their
    # preferences by chatting with the agent directly.

    async def send() -> None:
        question = text.value
        text.value = ''

        print("Sending question to agent...")

        with message_container:
            ui.chat_message(text=question, name='You', sent=True)
            response_message = ui.chat_message(name=config.openai_model_name, sent=False)
            ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

        response = ''
        with response_message:
            spin = ui.spinner()
            output = await nexus.chat("pat", question)
            ui.markdown(output)
            response_message.sent = True
            spin.delete()

        ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

    ui.page_title('Langgraph Example Chat')

    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('Chat')
        settings_tab = ui.tab('Settings')
    
    with ui.tab_panels(tabs, value=chat_tab).classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        with ui.tab_panel(chat_tab).classes('items-stretch'):
            message_container = ui.column().classes('w-full')

        with ui.tab_panel(settings_tab).classes('items-stretch'):
            ui.label('Settings')
            ui.input(label="OPENAI_API_URL", placeholder=config.openai_api_url, on_change=lambda e: setattr(config, 'openai_api_url', e.value))
            ui.input(label="OPENAI_API_KEY", password=True, on_change=lambda e: setattr(config, 'openai_api_key', e.value))
            ui.input(label="OPENAI_MODEL_NAME", placeholder=config.openai_model_name, on_change=lambda e: setattr(config, 'openai_model_name', e.value))
            ui.textarea(label="System Message", value=config.system_message, on_change=lambda e: setattr(config, 'system_message', e.value))

    with ui.footer():
        placeholder = 'Send a message here'
        text = ui.input(placeholder=placeholder).props('rounded outlined input-class=max-3 bg-color=white').classes('w-full self-center').on('keydown.enter', send)

    # The agent will ask the user for their preferences and
    # then find events that match those preferences.

ui.run(loop="asyncio")
# ui.run()