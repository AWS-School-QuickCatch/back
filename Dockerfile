# 베이스 이미지
FROM python:3.11-alpine

# 작업 디렉토리 설정
WORKDIR /app

# Python 패키지 설치를 위해 필요한 시스템 패키지 설치
RUN apk update && apk add --no-cache \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    postgresql-dev \
    build-base \
    libffi-dev \
    mariadb-dev \
    pkgconfig

# requirements.txt 파일을 복사하고 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 소스 복사
COPY . /app/

# 포트 노출
EXPOSE 8000

# 애플리케이션 시작 명령
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

