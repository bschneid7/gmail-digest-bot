FROM node:18-alpine as webbuild
WORKDIR /web
COPY web/package*.json ./
RUN npm ci || npm install
COPY web ./
RUN npm run build

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./
COPY --from=webbuild /web/dist /app/static/dist
EXPOSE 8000
ENV PORT=8000
CMD ["gunicorn", "-w", "2", "-k", "gthread", "-b", "0.0.0.0:8000", "app:app"]
