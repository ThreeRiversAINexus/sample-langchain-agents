# Use the official Python 3.10 runtime as a parent image
FROM python:3.10

# Set the working directory in the container to /foobar
# This is where the volume will be mounted
WORKDIR /app

# Install LangChain and its components
RUN pip install langchain \
    langchain-community \
    langchain-core \
    langchain-experimental

# Define the directory that can be mounted from the host.
# This is where the host's directory will be seen in the container.
VOLUME ["/app"]

# Instead of running app.py directly, start a bash shell to interact with.
# This allows the developer to run app.py or any other commands manually.
CMD ["/bin/bash"]

# Build and Use:
# docker build -t example_structured_chat_agent .
# docker run -it -v ./example_structured_chat_agent:/app example_structured_chat_agent