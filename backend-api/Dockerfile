# 1. 베이스 이미지 선택
FROM python:3.10-slim
ENV MODE=docker

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일 복사
COPY server.py .
COPY requirements.txt .

# 4. 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 포트 열기
EXPOSE 5000

# 6. 컨테이너 실행 시 명령어
CMD ["python", "server.py"]

