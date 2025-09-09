# Start from the official Rasa SDK base image
FROM rasa/rasa-sdk:3.6.2

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# --- FIX ---
# Switch to the root user to gain permissions for installing packages
USER root

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- FIX ---
# Switch back to the default non-root user for better security
USER 1001

CMD ["python", "-m", "rasa_sdk", "--actions", "actions", "--host", "0.0.0.0"]
