# Use official Python image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1 

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install netcat and verify installation
RUN apt-get update && apt-get install -y netcat-openbsd

# Copy the Django project
COPY . .

# Expose port for Django
EXPOSE 8000

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh
# Set the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Ensure database migrations are applied and static files are collected
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "E_commerce.wsgi:application"]
