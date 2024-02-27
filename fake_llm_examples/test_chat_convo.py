from langchain_community.llms.fake import FakeListLLM
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

test_user_messages = [
    "hello",
    "who are you?",
    "how are you?"
]
test_responses = [
    "The user is initiating a conversation with a greeting.",
    "I'm just a language model AI, I'm here to help you!",
    "I am well"
]
# https://python.langchain.com/docs/modules/memory/
prompt = ChatPromptTemplate(
    messages = [
        SystemMessagePromptTemplate.from_template(
            "We are testing the chat system"
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{user_message}")
    ]
)
memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True)

# https://api.python.langchain.com/en/latest/llms/langchain_community.llms.fake.FakeListLLM.html#langchain_community.llms.fake.FakeListLLM
fake_llm = FakeListLLM(responses=test_responses)

conversation = LLMChain(
    llm=fake_llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)

for message in test_user_messages:
    response = conversation({"user_message": message})
    print(response)

# output = fake_llm.invoke(messages)
# print(output)