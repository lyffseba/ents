# web/Dockerfile - Cloud Run ready for Ents Academy (XPRIZE)
# FastAPI + Gemini + agents. Use google base for good GC compat.
FROM python:3.12-slim

WORKDIR /app

# System deps for some scientific (jax etc optional in web; full pillars via download)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && rm -rf /var/lib/apt/lists/*

COPY web/requirements.txt* ./
# Fallback simple requirements if no lock
RUN pip install --no-cache-dir fastapi uvicorn[standard] jinja2 python-multipart stripe sqlalchemy apscheduler python-dotenv pydantic httpx google-generativeai

# Copy app
COPY web /app/web
COPY max_env/phases /app/max_env/phases  # for oracle reuse / curriculum

ENV PYTHONPATH=/app
ENV PORT=8080
# In Cloud Run, set GEMINI_API_KEY etc as secrets

CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8080"]
