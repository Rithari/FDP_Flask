# Use an official Python runtime as a parent image
FROM python:3.12.1-bookworm

# Install gcc (if not already available in the Python image)
RUN apt-get update && apt-get install -y gcc gdal-bin libgdal-dev

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Make port 4000 available to the world outside this container
EXPOSE 4000

# Define environment variable
ENV NAME World

# Run app.py when the container launches using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:4000", "app:app"]
