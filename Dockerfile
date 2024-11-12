FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

#ENV LANGCHAIN_API_KEY='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'
#ENV GROQ_API_KEY='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'

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
