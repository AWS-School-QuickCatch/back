gitignore
venv my_settings.py pycache

가상 환경 생성
python -m venv venv

가상 환경 활성화 (Windows 환경, cmd나 git bash에서)
.\venv\Scripts\activate 정상적으로 활성화 시 가상환경 진입: (venv)

의존성 설치 (venv)
pip install -r requirements.txt

Django 실행 (manage.py 위치에서)
py manage.py runserver

가상 환경에 필요한 패키지만 공유 (venv)
항상 가상환경에 필요한 패키지와 버전을 아래 명령어로 최신화 및 공유
pip freeze > requirements.txt

데이터베이스 연동 (manage.py 위치에서)
python manage.py makemigrations 
python manage.py migrate

종료 시 가상 환경 비활성화
deactivate
