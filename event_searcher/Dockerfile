# Use the official Python 3.11 runtime as a parent image
FROM python:3.11

# Set the working directory in the container to /foobar
# This is where the volume will be mounted
WORKDIR /app

COPY requirements.txt requirements.txt
COPY event_agent.py event_agent.py

# Install LangChain and its components
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN playwright install-deps
RUN playwright install

# Define the directory that can be mounted from the host.
# This is where the host's directory will be seen in the container.
VOLUME ["/app"]

# Instead of running app.py directly, start a bash shell to interact with.
# This allows the developer to run app.py or any other commands manually.
CMD ["/bin/bash"]

# Build and Use:
# Run ./build.sh then ./run.sh