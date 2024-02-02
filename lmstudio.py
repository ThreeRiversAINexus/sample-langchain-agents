import openai

def make_request(system_content, user_content):
    # Set up OpenAI API
    openai.api_base = "http://pats-upstairs-desktop.lan:1234/v1" # Point to the local server
    openai.api_key = "" # No need for an API key

    # Create a ChatCompletion request
    completion = openai.ChatCompletion.create(
        model="local-model", # This field is currently unused
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
    )

    # Print the response
    print(completion.choices[0].message)

# Define system content with ||| instead of backticks
system_content = """Respond to the human as helpfully and accurately as possible. You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

|||
{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}
|||

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
|||
$JSON_BLOB
|||
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
|||
{
  "action": "Final Answer",
  "action_input": "Final response to human"
}
|||

Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:
|||$JSON_BLOB|||
then Observation"""

# Define user content
user_content = "Introduce yourself."

# Make the request
make_request(system_content, user_content)
