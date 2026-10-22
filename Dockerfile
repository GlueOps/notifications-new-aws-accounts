FROM python:3.15-slim@sha256:490c3463f3766091067a01528e6be3208104eebcca11a306beab5de9672ee893

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
