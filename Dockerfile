FROM seleniumbase/seleniumbase:latest

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY main.py .

# Expose the port
EXPOSE 8000

# Start the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]