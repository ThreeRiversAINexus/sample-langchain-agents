from dotenv import load_dotenv
import os

# Simply add OPENAI_API_KEY=... to .env
# Then launch with `python structured_chat.py`

load_dotenv()

from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_openai import ChatOpenAI
from langchain.agents import tool
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts.chat import ChatPromptTemplate, MessagesPlaceholder

@tool
def get_word_length(word: str) -> int:
    """ Returns the length of a word """
    return len(word)

tools = [get_word_length]

system = '''Respond to the human as helpfully and accurately as possible. You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}

Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation'''

human = '''

{input}

{agent_scratchpad}

(reminder to respond in a JSON blob no matter what)'''

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", human),
    ]
)

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")

agent = create_structured_chat_agent(llm, tools, prompt)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    # verbose=True,
    handle_parsing_errors=True,
    memory=memory,
)

while True:
    user_input = input("User: ")
    chat_history = memory.buffer_as_messages
    response = agent_executor.invoke({
        "input": user_input,
        "chat_history": chat_history,
    })
    print("Agent:", response['output'])

# Example chat
# $ python structured_chat.py 
# User: how are ya
# Agent: I'm here to assist you with any questions you have.
# User: how long is the word langchain
# Agent: The word 'langchain' is 9 characters long.
# User: whats the longest word you know
# Agent: Pneumonoultramicroscopicsilicovolcanoconiosis
# User: how long is that word
# Agent: 45
# User: what was the first word i asked you to count the length of
# Agent: langchain
# User: