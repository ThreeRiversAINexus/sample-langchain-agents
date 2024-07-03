# Use the official Python 3.10 runtime as a parent image
FROM python:3.10

# Set the working directory in the container to /foobar
# This is where the volume will be mounted
WORKDIR /app

COPY requirements.txt requirements.txt
COPY main.py main.py

# Install LangChain and its components
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Define the directory that can be mounted from the host.
# This is where the host's directory will be seen in the container.
VOLUME ["/app"]

# Instead of running app.py directly, start a bash shell to interact with.
# This allows the developer to run app.py or any other commands manually.
CMD ["/bin/bash"]

# Build and Use:
# Run ./build.sh then ./run.sh