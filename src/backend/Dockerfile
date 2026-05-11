FROM python:3.12-slim

WORKDIR /app

# Ensure CA certificates are present and basic tools for networking
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    ca-certificates \
    curl \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Allow overriding PyPI index at build time (use a mirror in restricted networks)
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_INDEX_URL=${PIP_INDEX_URL}
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

COPY pyproject.toml .
# Upgrade pip tooling first and configure index for subsequent installs to avoid
# repeated metadata downloads from the default PyPI which may be unreliable here.
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip config set global.index-url ${PIP_INDEX_URL} \
    && pip config set global.trusted-host ${PIP_TRUSTED_HOST} \
    # Install cryptography early so DB auth methods (caching_sha2_password)
    # work when connecting to MySQL. Installing here avoids runtime errors
    # when async MySQL drivers attempt to use RSA encryption.
    && pip install --no-cache-dir cryptography \
    && pip install --no-cache-dir .

COPY src/ src/

EXPOSE 8000

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
