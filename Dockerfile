FROM node:22-alpine AS frontend
WORKDIR /app/frontend-react
COPY frontend-react/package*.json ./
RUN npm ci
COPY frontend-react/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY . /app
COPY --from=frontend /app/frontend-react/dist /app/frontend-react/dist

ENV PYTHONPATH=/app/backend
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Run from backend so the root-level Streamlit app.py cannot shadow app.main.
WORKDIR /app/backend
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
