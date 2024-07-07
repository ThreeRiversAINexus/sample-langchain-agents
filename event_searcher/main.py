from nicegui import ui

# Singleton class for configuration
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.api_key_1 = ""
            cls._instance.api_key_2 = ""
            cls._instance.url = ""
        return cls._instance

@ui.page('/')
def main():
    config = Config()

    # The purpose of this application is to find events that
    # the user might like to go to. The user can input their
    # preferences by chatting with the agent directly.

    with ui.column():
        ui.label('Welcome to the event finder!')
        ui.label('Please enter your preferences below:')

    # The agent will ask the user for their preferences and
    # then find events that match those preferences.

ui.run()