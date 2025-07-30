FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install OS deps first (keeps layer cache stable)
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg libsm6 libxext6 unzip curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# (Optional) Install AWS CLI v2 *inside* the image only if your app needs it at runtime.
# Most CI/CD flows should install AWS CLI on the runner, not in the app image.
RUN curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip \
 && unzip -q awscliv2.zip \
 && ./aws/install \
 && rm -rf aws awscliv2.zip

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app

CMD ["python", "app.py"]
