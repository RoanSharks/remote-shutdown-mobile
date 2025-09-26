# Dockerfile for building Android APK
FROM ubuntu:20.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    zip \
    unzip \
    openjdk-8-jdk \
    wget \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

# Install Python packages
RUN pip3 install buildozer cython

# Create working directory
WORKDIR /app

# Copy your app files
COPY . .

# Build the APK
CMD ["buildozer", "android", "debug"]