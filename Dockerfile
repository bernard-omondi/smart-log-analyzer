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

# Install the package
RUN pip install --no-cache-dir -e ".[dev]"

# Set the default command (you can override this)
ENTRYPOINT ["python", "-m", "src.ingest"]

# Default arguments (override with --help, --verbose, etc.)
CMD ["--help"]
