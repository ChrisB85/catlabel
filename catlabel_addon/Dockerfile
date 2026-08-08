FROM python:3.11-slim

# Supervisor passes this to every add-on build; unused here because the base
# image is pinned rather than derived from the Home Assistant base images.
ARG BUILD_FROM

# Bump to build from a tag or branch other than the default.
ARG CATLABEL_REF=master

ENV PYTHONUNBUFFERED=1 \
    CATLABEL_PORT=8099 \
    CATLABEL_DATA_DIR=/data \
    CATLABEL_NO_BROWSER=1 \
    CATLABEL_INGRESS_ONLY=1

# The add-on build context is this directory only, so the application is
# fetched from the repository rather than copied from the parent directory.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && git clone --depth 1 --branch "${CATLABEL_REF}" \
        https://github.com/ChrisB85/catlabel.git /app \
    && apt-get purge -y --auto-remove git \
    && rm -rf /var/lib/apt/lists/* /app/.git

WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "catlabel"]
