FROM python:3.10

WORKDIR /app

# Install dependencies from your requirements.txt file
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set the entry point for the application
CMD ["python", "services/extraction_service.py"]