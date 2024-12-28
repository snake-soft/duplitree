FROM python:3.12.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY src/duplitree /app/duplitree
WORKDIR /app/duplitree
RUN mkdir -p /app/static_root && chown 10000:10000 /app/static_root
RUN mkdir -p /mnt && chown 10000:10000 /mnt
USER 10000:10000
