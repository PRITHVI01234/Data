# Use Python 3.11 as the base image
FROM python:3.11-slim-bullseye

# Install OpenJDK 17
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Command to run the application
CMD streamlit run Home.py --server.port $PORT --server.address 0.0.0.0