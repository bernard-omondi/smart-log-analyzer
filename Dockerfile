# Use the official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (if any)
RUN apt-get update && apt-get install -y \
	build-essential \
	&& rm -rf /var/lib/apt/lists/*

# Copy the project files into the container
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY scripts/ ./scripts/

# Install the package with longer timeout
RUN pip install --no-cache-dir -e ".[dev]" --timeout 100

# Run the FastAPI server
ENTRYPOINT ["uvicorn", "src.api:app"]
CMD ["--host", "0.0.0.0", "--port", "10000"]
