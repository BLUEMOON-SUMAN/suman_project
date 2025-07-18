# backend/Dockerfile (suman_project/suman_pj_back 폴더 안에 생성)
FROM python:3.11-alpine

# 컨테이너 내에서 작업할 디렉토리를 설정합니다.
WORKDIR /app

# 호스트의 requirements.txt 파일을 컨테이너의 /app 디렉토리로 복사합니다.
# 이 파일은 suman_pj_back 폴더 안에 있어야 합니다.
COPY requirements.txt /app/

# 필요한 파이썬 패키지들을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 호스트의 현재 디렉토리(suman_pj_back/)의 모든 내용을 컨테이너의 /app 디렉토리로 복사합니다.
# 주의: Docker Compose의 volumes 설정을 사용하면 개발 시에는 코드가 자동으로 동기화되지만,
# 배포용 이미지를 만들 때는 이 COPY . /app/ 명령이 필요합니다.
# 현재는 개발 편의를 위해 볼륨을 주로 쓰겠지만, 이미지 빌드 관점에서 필요하니 넣어둡시다.
COPY . /app/suman_pj_back

WORKDIR /app/suman_pj_back

# Django 애플리케이션이 외부에서 접근할 포트를 지정합니다.
EXPOSE 8000

# CMD 명령은 docker-compose.yml에서 오버라이드할 것이므로 여기에선 주석 처리하거나 생략 가능
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]