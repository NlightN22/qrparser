# ---- Base image with common env ----
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Make venv globally available
    VENV_PATH="/opt/venv" \
    # Force UTF-8
    LC_ALL=C.UTF-8 LANG=C.UTF-8

# Create a non-root user
RUN adduser --disabled-password --gecos "" --home /home/appuser appuser

WORKDIR /app

# ---- Builder: install into a virtualenv ----
FROM base AS builder
RUN python -m venv "${VENV_PATH}"
ENV PATH="${VENV_PATH}/bin:${PATH}"

COPY pyproject.toml README.md /app/
RUN pip install --upgrade pip && pip install . ".[server]"

# Copy source for editable reinstall
COPY src /app/src
RUN pip install --no-deps .

# ---- Tests: install test deps and run pytest (build fails on test failure) ----
FROM builder AS test
ENV PATH="${VENV_PATH}/bin:${PATH}"

# Install test extras
COPY pyproject.toml /app/pyproject.toml
RUN pip install ".[test]"

# Copy tests and run them
COPY tests /app/tests
# If you want coverage artifact in CI, you can also write to /tmp
RUN pytest -q

# ---- Runtime: copy only venv + app code ----
FROM base AS runtime
COPY --from=builder ${VENV_PATH} ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:${PATH}"
COPY --from=builder /app /app
COPY docker/healthcheck.py /usr/local/bin/healthcheck.py
RUN chmod +x /usr/local/bin/healthcheck.py

USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python /usr/local/bin/healthcheck.py
ENV QR_HTTP_WORKERS=2 QR_HTTP_HOST=0.0.0.0 QR_HTTP_PORT=8000 QR_LOG_LEVEL=INFO
CMD ["python", "-m", "qrparser.web.serve"]
