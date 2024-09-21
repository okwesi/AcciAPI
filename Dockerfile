# Use the official Python image as a parent image
FROM public.ecr.aws/docker/library/python:3.11


# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="$VIRTUAL_ENV/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for pycurl and virtual environment creation
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libssl-dev \
 && rm -rf /var/lib/apt/lists/*

# Create a virtual environment and use it
RUN python -m venv $VIRTUAL_ENV

# Ensure pip, setuptools, and wheel are up to date in venv
RUN pip install --upgrade pip setuptools wheel

# First, copy only requirements.txt
COPY requirements.txt .

# Install project dependencies from requirements.txt into the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# If pycurl is not in your requirements.txt, install it separately
# It's installed in the virtual environment by default due to the ENV PATH setup
RUN pip install pycurl

# Copy entrypoint script and give it execution permissions
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy the rest of the project files into the container
COPY . .

# Expose port 8000 for the Daphne server
EXPOSE 8000

# Use entrypoint.sh to run the server
CMD sh -c "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"