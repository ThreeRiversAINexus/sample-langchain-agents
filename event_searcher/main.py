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
            # This is basically your session ID
            cls._instance.thread_id = str(uuid.uuid4())
            # These are needed for ChatOpenAI
            cls._instance.openai_api_key = os.environ.get('OPENAI_API_KEY')
            cls._instance.openai_api_url = "https://api.openai.com/v1/"
            cls._instance.openai_model_name = os.environ.get('OPENAI_MODEL_NAME', 'gpt-4o')
            # This is the system message that the LLM will use
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

import asyncio
import nest_asyncio

class State(TypedDict):
    messages: Annotated[list, add_messages]

from langchain_openai import ChatOpenAI 

from my_utils.navigate import NexusNavigateTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
import uuid

class Nexus:
    def __init__(self, config: Config):
        self.config = config

        self.tools = []
        self.tools += self.setup_playwright()
        self.tools += [self.setup_serper()]

        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            base_url=self.config.openai_api_url,
            model=self.config.openai_model_name,
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

        self.debugging_output = asyncio.Queue()

    async def get_debugging_output(self, continuous=False) -> str:
        if continuous:
            while True:
                item = await self.debugging_output.get()
                yield item
                self.debugging_output.task_done()
        else:
            message = await self.debugging_output.get()
            yield 
        while True:
            item = await self.debugging_output.get()
            yield item
            self.debugging_output.task_done()

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

        these_messages = [
            SystemMessage(content=self.config.system_message),
            *state["messages"],
            HumanMessagePromptTemplate.from_template("{message}")
        ]
        my_prompt = ChatPromptTemplate.from_messages(these_messages)

        chain = my_prompt | self.llm

        print(state["messages"])
        return {"messages": [await chain.ainvoke(input={"message": state["messages"][-1].content})]}

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
    
    def should_reflect(self, state: State) -> Literal["chatbot", "__end__"]:
        """Return the next node to execute."""
        last_message = state["messages"][-1]
        # Use an LLM to evaluate the message
        # If the message is good enough, we finish
        # If the message is not good enough, we reflect
        # the message and try again, expanding on the previous message?
        # Otherwise if there is, we continue
        return "chatbot"
    
    async def chat(self, message):
        response = ''
        print("Chatting with agent...")
        async for event in self.graph.astream({"messages": [message]},
            {"configurable": {"thread_id": self.config.thread_id}}):
            print("New event")
            for value in event.values():
                print("Value: ", value)
                await self.debugging_output.put(f"Value: {value}")
                for message in value["messages"]:
                    # If the message is an AIMessage, we want to display it
                    if isinstance(message, AIMessage):
                        yield message.content
                        # response += message.content + '\n'
                        # ui.markdown(f"{response}")
                    # If the message is a ToolMessage, we want to log it
                    if isinstance(message, ToolMessage):
                        print(message)

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
            output = ui.markdown()
            spin = ui.spinner()
            # I should find out how to
            # pass through the async iterable
            # so we can stream the output to the UI
            async for output_chunk in nexus.chat(question):
                output.content += output_chunk
                # with debugging_output:
                #     async for debugging_output_chunk in nexus.get_debugging_output():
                #         debugging_output.text += debugging_output_chunk
            response_message.sent = True
            spin.delete()

        ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

    ui.page_title('Langgraph Example Chat')

    with ui.header(), ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('Chat')
        settings_tab = ui.tab('Settings')
        debugging_tab = ui.tab('Debugging')
    
    with ui.tab_panels(tabs, value=chat_tab).classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        with ui.tab_panel(chat_tab).classes('items-stretch'):
            message_container = ui.column().classes('w-full')

        with ui.tab_panel(settings_tab).classes('items-stretch'):
            ui.label('Settings')
            ui.input(label="OPENAI_API_URL", placeholder=config.openai_api_url, on_change=lambda e: setattr(config, 'openai_api_url', e.value))
            ui.input(label="OPENAI_API_KEY", password=True, on_change=lambda e: setattr(config, 'openai_api_key', e.value))
            ui.input(label="OPENAI_MODEL_NAME", placeholder=config.openai_model_name, on_change=lambda e: setattr(config, 'openai_model_name', e.value))
            ui.textarea(label="System Message", value=config.system_message, on_change=lambda e: setattr(config, 'system_message', e.value))

        with ui.tab_panel(debugging_tab).classes('items-stretch'):
            ui.label('Debugging')
            logging_container = ui.column().classes('w-full')
            # with logging_container:
            #     debugging_output = ui.label()

    with ui.footer():
        placeholder = 'Send a message here'
        text = ui.input(placeholder=placeholder).props('rounded outlined input-class=max-3 bg-color=white').classes('w-full self-center').on('keydown.enter', send)

    # The agent will ask the user for their preferences and
    # then find events that match those preferences.

ui.run(loop="asyncio") # playwright needs asyncio and nest_asyncio.apply()
# ui.run()