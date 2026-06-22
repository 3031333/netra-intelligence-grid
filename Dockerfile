# 1. Start with a lightweight Linux Python environment
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all your Python code into the container
COPY . .

# 5. Expose the default port (for local testing)
EXPOSE 8000

# 6. The command to boot the server (Cloud-Aware Port Binding)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}