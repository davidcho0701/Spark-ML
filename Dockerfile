FROM python:3.11

# Java 및 nc 설치 (PySpark + netcat 실습용)
RUN apt-get update && apt-get install -y \
    default-jdk \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Java 환경변수 설정
ENV JAVA_HOME=/usr/lib/jvm/default-java

# PySpark 및 라이브러리 설치
RUN pip install --no-cache-dir \
    pyspark==3.5.0 \
    numpy \
    pandas

WORKDIR /app



