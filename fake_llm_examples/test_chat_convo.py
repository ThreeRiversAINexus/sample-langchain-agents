from langchain_community.llms.fake import FakeListLLM
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
import unittest

test_chats = {
    "hello": "The user is initiating a conversation with a greeting.",
    "who are you?": "I'm just a language model AI, I'm here to help you!",
    "how are you?": "I am well"
}
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
fake_llm = FakeListLLM(responses=[chat for chat in test_chats.values()])

conversation = LLMChain(
    llm=fake_llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)

class TestChatConvo(unittest.TestCase):
    def test_chat_convo(self):
        ideal_chat_history = []
        for message in test_chats.keys():
            response = conversation.invoke({"user_message": message})
            self.assertEqual(response["text"], test_chats[message])
            self.assertListEqual(response["chat_history"], ideal_chat_history)
            # We must insert these before the next iteration
            # because the chat_history is blank for the first
            # message
            ideal_chat_history += [
                HumanMessage(content=message),
                AIMessage(content=test_chats[message])
            ]
    
if __name__ == '__main__':
    unittest.main()