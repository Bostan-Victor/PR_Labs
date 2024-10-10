# Step 1: Use a Python base image
FROM python:3.8-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container
COPY . .

RUN pip install -r requirements.txt

# Step 5: Expose the port you will use (change this if you’re using another port)
EXPOSE 8000

# Step 6: Command to run the lab1_sockets.py script
CMD ["python", "lab1_sockets.py"]
