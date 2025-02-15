FROM python:3.9-slim

# Install system dependencies needed for Pillow, Face Recognition, and Git
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    git \
 && rm -rf /var/lib/apt/lists/*

# Optionally, verify that Git is installed
RUN git --version

WORKDIR /app

# Copy project files into the container
COPY . /app

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install flask numpy pillow requests face_recognition waitress && \
    pip install git+https://github.com/ageitgey/face_recognition_models

# Expose the port the app runs on
EXPOSE 8080

# Run the application using waitress
CMD ["python", "-m", "waitress", "--listen=0.0.0.0:8080", "app:app"]