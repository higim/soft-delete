FROM python:3.12

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements first for caching
COPY ./requirements.txt /app/requirements.txt

# 5. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the app code
COPY ./ /app/

# 7. Expose FastAPI port
EXPOSE 8000

# 8. Run Uvicorn with auto-reload (optional for dev)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
