FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Provided at `docker run` time via -e, not baked into the image.
ENV GROQ_API_KEY=""
ENV SLACK_WEBHOOK_URL=""
ENV EVAL_MODEL="llama-3.1-8b-instant"
ENV MAX_REQUESTS_PER_MINUTE="28"
ENV MAX_TOKENS_PER_MINUTE="5500"

ENTRYPOINT ["python", "scripts/run_eval.py"]
CMD ["v1"]
