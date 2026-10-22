FROM python:3.14-slim@sha256:0b566a9f30a60730df33c26ac62dedb55393d8814645cd03543b67bf8987f3a1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set working directory to src for imports
WORKDIR /app/src

# Run the main script
CMD ["python", "main.py"]
