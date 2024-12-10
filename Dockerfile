# Use the official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the application files
COPY script.py /app/script.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the script
CMD ["python", "script.py"]