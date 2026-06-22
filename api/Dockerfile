# syntax=docker/dockerfile:1

# ---- Stage 1: builder (installs deps into a venv) --------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- Stage 2: runtime (slim + headless Chromium for PDF export) -----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Non-root runtime user.
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv

# Install Chromium + its OS dependencies for server-side PDF rendering.
# (Heavier image; this is the cost of vector PDF export via Playwright.)
RUN python -m playwright install --with-deps chromium \
    && chmod -R a+rx /ms-playwright

COPY alembic.ini ./alembic.ini
COPY migrations ./migrations
COPY app ./app
COPY entrypoint.sh ./entrypoint.sh
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
