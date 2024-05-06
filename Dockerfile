# Use a Python 3.8 runtime as a base image
FROM python:3.8
WORKDIR /app

# Copy the requirements file and install the necessary packages
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Copy the source code, configuration file, and database file
COPY . .

# Start the bot
CMD ["python", "main.py"]
