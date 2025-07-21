# suman_project/suman_pj_back/create_superuser.py

import os
import django
from django.conf import settings
from django.contrib.auth import get_user_model
from decouple import config # config 함수를 사용하기 위해 임포트

# Django 설정을 로드합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suman_pj_back.settings')
django.setup()

User = get_user_model()

# 환경 변수에서 슈퍼유저 정보를 config() 함수로 가져옵니다.
# 기본값은 설정하지 않는 것이 좋습니다. 없으면 경고 메시지가 뜨도록 합니다.
SUPERUSER_USERNAME = config('DJANGO_SUPERUSER_USERNAME', default=None)
SUPERUSER_EMAIL = config('DJANGO_SUPERUSER_EMAIL', default=None)
SUPERUSER_PASSWORD = config('DJANGO_SUPERUSER_PASSWORD', default=None)

# 모든 슈퍼유저 환경 변수가 설정되어 있는지 확인합니다.
if not all([SUPERUSER_USERNAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD]):
    print("WARNING: Superuser environment variables (DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD) not set. Skipping superuser creation.")
    print("Please set these in Render's Environment Variables.")
else:
    # 해당 사용자 이름의 슈퍼유저가 이미 존재하는지 확인합니다.
    if not User.objects.filter(username=SUPERUSER_USERNAME).exists():
        print(f"Creating superuser '{SUPERUSER_USERNAME}'...")
        try:
            User.objects.create_superuser(SUPERUSER_USERNAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD)
            print("Superuser created successfully.")
        except Exception as e:
            print(f"ERROR: Failed to create superuser: {e}")
            # 슈퍼유저 생성 실패 시 프로세스를 종료하지 않도록 합니다.
    else:
        print(f"Superuser '{SUPERUSER_USERNAME}' already exists. Skipping creation.")