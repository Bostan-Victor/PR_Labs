# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose both the Flask and WebSocket ports
EXPOSE 5000
EXPOSE 6790

# Make the start script executable
RUN chmod +x start.sh

# Run the start script
CMD ["./start.sh"]
