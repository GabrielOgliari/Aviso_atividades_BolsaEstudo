# Use the base image with Python 3.12 on Debian
FROM python:3.12-slim

# Create the directory for the application
WORKDIR /app

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Create a non-root user and set ownership of the /app directory
RUN useradd -m pyuser && chown -R pyuser:pyuser /app

# Switch to the non-root user
USER pyuser

# Command to run the application
CMD ["python", "aviso.py"]
