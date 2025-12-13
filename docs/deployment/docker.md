# Docker Deployment Guide

Deploy CV-Mindcare using Docker containers.

## Quick Start

```bash
# Coming soon
docker pull cvmindcare/cv-mindcare:latest
docker run -p 8000:8000 -p 5173:5173 cvmindcare/cv-mindcare
```

## Building from Source

```bash
# Build image
docker build -t cv-mindcare .

# Run container
docker run -d \
  --name cv-mindcare \
  -p 8000:8000 \
  -p 5173:5173 \
  -v $(pwd)/config:/app/config \
  cv-mindcare
```

## Docker Compose

```yaml
version: '3.8'
services:
  cv-mindcare:
    build: .
    ports:
      - "8000:8000"
      - "5173:5173"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    environment:
      - CVMINDCARE_API_SERVER_PORT=8000
```

_Docker support is planned for v1.0.0_
