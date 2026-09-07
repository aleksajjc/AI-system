FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn "psycopg[binary]" python-dotenv "supabase==2.31.0"

COPY main.py database.py authentication.py ./

EXPOSE 3000

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-3000}"]
