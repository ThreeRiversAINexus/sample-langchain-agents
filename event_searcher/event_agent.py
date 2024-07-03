import os
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI

class Beliefs():
    def create_chat_llm(self):
        return ChatOpenAI(model='gpt-3.5-turbo')

    def today(self):
        import datetime
        return datetime.datetime.now().strftime("%B %d, %Y")

class Intentions():
    def search_events(self, description, agent):
        search_tool = SerperDevTool()
        return Task(
            description=description,
            tools=[search_tool],
            agent=agent,
            expected_output="""
            A custom tailor-made article summarizing events that the user may find interesting that are upcoming, including their date, time, location, cost if any, and a description.
            """,
            verbose=True
        )

class EventRecommendationSystem():
    def __init__(self, beliefs=Beliefs(), intentions=Intentions()):
        self.beliefs = beliefs
        self.intentions = intentions

    def event_finding_agent(self):
        llm = self.beliefs.create_chat_llm()

        return Agent(
            role='Interesting Event Finding Agent',
            goal='Find upcoming and annual events that are interesting',
            backstory="""Agent who is an expert at recommending events, searching for events, planning events, and understanding how events are advertised, and custom tailoring them to a user
            """,
            llm=llm,
            verbose=True
        )

    def find_events(self, description):
        finder = self.event_finding_agent()
        today = self.beliefs.today()
        description = f'{description}. Today is {today}. Events MUST be after {today}.'
        task = self.intentions.search_events(description, finder)

        try:
            c = Crew(
                agents=[finder],
                tasks=[task],
                verbose=2
            )

            return c.kickoff()
        except:
            import traceback
            traceback.print_exc()
            return "There was an error"

def run():
    recommender = EventRecommendationSystem()
    events = recommender.find_events("Live music in Pittsburgh, PA")
    print(events)

run()