# COPD 선별 시스템 (copd-prediction)

건강검진 데이터를 기반으로 폐활량검사 권고 우선순위를 선별하는 임상 의사결정 보조 시스템.
이 모델은 진단 도구가 아니며, 의사의 검사 처방 결정을 보조하는 역할을 합니다.

## 프로젝트 구조

```
copd-prediction/
├── config/          # Django 프로젝트 설정 (settings, urls)
├── accounts/        # User, PatientProfile, DoctorProfile
├── screening/        # Questionnaire, HealthRecord, PredictionResult, ClinicalDecision
├── daily_care/       # DailyLog (일상 체크인)
├── appointments/     # AppointmentRequest (검사 예약 요청)
├── benchmarks/       # Benchmark (연령대×성별 비교 기준값)
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## 처음 셋업하는 방법

### 1. 저장소 클론

```bash
git clone <repo-url>
cd copd-prediction
```

### 2. 가상환경 생성 및 활성화(python 3.12 버전 통일 필요)

```bash
python -m venv .venv

# Windows (Git Bash)
source .venv/Scripts/activate

# Windows (cmd)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

`.env.example`을 복사해서 `.env` 파일을 만들고, 본인 MySQL 환경에 맞게 값을 채웁니다.

```bash
cp .env.example .env
```

`.env` 파일은 절대 git에 올리지 않습니다 (`.gitignore`에 등록되어 있음). DB 비밀번호 등 민감정보가 들어있기 때문입니다.

### 5. 서버 실행

```bash
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000/admin/` 접속해 정상 작동을 확인합니다.

## 패키지를 새로 설치했다면

```bash
pip freeze > requirements.txt
```

`requirements.txt`를 갱신한 뒤 커밋해서 팀원과 공유합니다.

## 모델(models.py)을 수정했다면

```bash
python manage.py makemigrations
python manage.py migrate
```

새로 생성된 `migrations/000X_xxxx.py` 파일도 함께 커밋합니다.
