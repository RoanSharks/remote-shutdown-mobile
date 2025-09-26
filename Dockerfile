# Dockerfile - Direct P4A approach (bypass buildozer downloads)
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    zip \
    unzip \
    openjdk-11-jdk \
    wget \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Create builduser
RUN useradd -m -s /bin/bash builduser
USER builduser
WORKDIR /home/builduser

# Install Python packages
RUN pip3 install --user cython==0.29.33 sh==2.0.6

# Set up Android SDK in standard location
ENV ANDROID_HOME=/home/builduser/android-sdk
ENV ANDROID_SDK_ROOT=/home/builduser/android-sdk
ENV PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/build-tools/29.0.3

# Download and install Android SDK
RUN mkdir -p $ANDROID_SDK_ROOT && \
    cd /home/builduser && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip -q commandlinetools-linux-9477386_latest.zip && \
    mv cmdline-tools $ANDROID_SDK_ROOT/cmdline-tools-temp && \
    mkdir -p $ANDROID_SDK_ROOT/cmdline-tools && \
    mv $ANDROID_SDK_ROOT/cmdline-tools-temp $ANDROID_SDK_ROOT/cmdline-tools/latest && \
    rm commandlinetools-linux-9477386_latest.zip

# Pre-accept licenses
RUN mkdir -p $ANDROID_SDK_ROOT/licenses && \
    echo "24333f8a63b6825ea9c5514f83c2829b004d1fee" > $ANDROID_SDK_ROOT/licenses/android-sdk-license && \
    echo "84831b9409646a918e30573bab4c9c91346d8abd" > $ANDROID_SDK_ROOT/licenses/android-sdk-preview-license

# Install SDK components
RUN $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --update && \
    $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager \
    "platform-tools" \
    "build-tools;29.0.3" \
    "platforms;android-29" \
    "platforms;android-28" \
    "platforms;android-33"

# Download and install Android NDK r21b
RUN cd /home/builduser && \
    wget -q https://dl.google.com/android/repository/android-ndk-r21b-linux-x86_64.zip && \
    unzip -q android-ndk-r21b-linux-x86_64.zip && \
    rm android-ndk-r21b-linux-x86_64.zip

ENV ANDROID_NDK_ROOT=/home/builduser/android-ndk-r21b
ENV PATH=$PATH:$ANDROID_NDK_ROOT

# Install Python-for-Android directly
# Install buildozer and python-for-android
RUN pip3 install --user buildozer python-for-android

# Verify aidl is available
RUN ls -la $ANDROID_SDK_ROOT/build-tools/29.0.3/aidl

# Create app directory and copy files
WORKDIR /app
COPY --chown=builduser:builduser . .

# Build APK with buildozer using our pre-installed SDK/NDK
CMD ["bash", "-c", "export ANDROID_HOME=/home/builduser/android-sdk && export ANDROID_SDK_ROOT=/home/builduser/android-sdk && export ANDROID_NDK_HOME=/home/builduser/android-ndk-r21b && export ANDROID_NDK_ROOT=/home/builduser/android-ndk-r21b && export ANDROID_NDK=/home/builduser/android-ndk-r21b && export PATH=$PATH:/home/builduser/.local/bin && echo 'Using buildozer with pre-installed components...' && cd /app && buildozer android debug --profile=buildozer_simple.spec && echo 'Build complete!' && ls -la bin/*.apk || echo 'No APK found' && find . -name '*.apk' -type f || echo 'No APK anywhere'"]