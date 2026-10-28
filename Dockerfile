# syntax=docker/dockerfile:1

# ---- Stage 1: install dependencies into a separate prefix ----
FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: minimal runtime image ----
FROM python:3.12-slim AS runtime

# OpenShift runs containers with an arbitrary non-root UID in the root group
# (GID 0). Create an unprivileged user for local runs; on OpenShift the UID
# will be different, so every path the app writes to must be writable by GID 0.
RUN useradd --uid 1001 --gid 0 --create-home --shell /bin/bash appuser

WORKDIR /app
COPY --from=build /install /usr/local
COPY --chown=1001:0 app.py .

# /data holds tasks.json. Owned by GID 0 and group-writable (g=u) so that any
# UID in the root group - 1001 locally, a random one on OpenShift - can write.
RUN mkdir /data \
 && chown -R 1001:0 /app /data \
 && chmod -R g=u /app /data

ENV PORT=8080 \
    DATA_DIR=/data \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080
USER 1001

# gunicorn: a production WSGI server (the Flask dev server is for development only).
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]
