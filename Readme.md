# 🫁 COPD Screening Service

> 건강검진 데이터를 기반으로 폐활량검사 권고 우선순위를 선별하는 임상 의사결정 보조 시스템

---

## 📌 프로젝트 개요

매년 받는 건강검진 데이터(문진 + 검진수치)만으로 COPD(만성폐쇄성폐질환) 검사가 필요한 환자를
선별하는 서비스입니다. 환자가 검진 결과를 입력하면 학습된 머신러닝 모델이 폐활량검사 권고 점수를
산출하고, 의사가 이를 검토해 최종 검사 권고 여부를 판단합니다.

> ⚠️ **이 시스템은 진단 도구가 아닙니다.** 모델이 산출하는 값은 "COPD 위험확률"이 아니라
> **폐활량검사(스파이로메트리)를 받아보는 것이 좋을지를 가리키는 권고 점수**입니다.
> 실제 진단은 폐활량검사와 의사의 최종 검토를 거쳐야 합니다.

---

## 🎯 분석 목표

1. 문진 + 검진수치 26개 변수로 폐활량검사 권고 점수를 산출하는 분류 모델 구축
2. 단순 점수 산출을 넘어, 어떤 변수가 점수에 영향을 미쳤는지 환자가 직접 확인 가능하도록 설명력 확보
3. 환자가 흡연 등 생활습관 변화를 가정해볼 수 있는 What-if 시뮬레이션 제공
4. 동일 연령대·성별 평균과 비교해 본인 수치의 상대적 위치를 직관적으로 파악
5. 검사 예약부터 일상 기록까지, 선별 이후의 케어 흐름까지 포괄하는 서비스 구현

---

## 🛠️ 기술 스택

![Django](https://img.shields.io/badge/Django-6.0.6-092E20?logo=django)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-STRICT__TRANS__TABLES-4479A1?logo=mysql&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-Logistic_Regression-F7931E?logo=scikitlearn&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4.0-FF6384?logo=chartdotjs&logoColor=white)
![Google Cloud Vision](https://img.shields.io/badge/Google_Cloud_Vision-OCR-4285F4?logo=googlecloud&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-Reverse_Proxy-009639?logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-WSGI-499848?logo=gunicorn&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?logo=githubactions&logoColor=white)

---

## 📁 프로젝트 구조

```
copd-prediction/
│
├── config/             # Django 프로젝트 설정 (settings, urls, wsgi)
├── common/             # 전역 미들웨어, 유틸리티, 검증 정규식
│
├── accounts/           # User / PatientProfile / DoctorProfile
│                        # 인증, 역할 분기, 대시보드 진입점
│
├── screening/           # Questionnaire / HealthRecord
│                        # PredictionResult / ClinicalDecision
│                        # ML 모델 추론, OCR 처리, What-if 엔드포인트
│
├── daily_care/          # DailyLog — 일상 체크인 (중복 방지)
├── appointments/        # AppointmentRequest — 검사 예약 (동시성 제어)
├── benchmarks/          # Benchmark — 연령대×성별 비교, 위험요인 시각화
├── content/             # HealthTip / BreathingExercise / FAQ
│
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🧬 시스템 아키텍처

```
[사용자 브라우저]
        │ HTTPS (443)
        ▼
    ┌─────────┐
    │  Nginx  │── 정적 파일(CSS/JS/이미지) 직접 서빙, SSL 처리
    └────┬────┘
         │ Unix Socket
         ▼
    ┌──────────┐
    │ Gunicorn │── WSGI 서버, workers=2
    └────┬─────┘
         ▼
    ┌──────────────────┐
    │ Django Application │── ML Model(.pkl) · OCR API 연동
    └────────┬──────────┘
             ▼
         ┌───────┐
         │ MySQL │
         └───────┘
```

ML 모델은 워커 프로세스 시작 시 모듈 최상단에서 단 1회만 메모리에 로드되고,
이후 모든 추론 요청은 디스크 재접근 없이 메모리에 상주한 모델을 그대로 재사용합니다.

---

## 🗃️ ERD 핵심 흐름

```
User ──1:1── PatientProfile / DoctorProfile

PatientProfile ──1:N── Questionnaire, HealthRecord
                          │
                          ▼
                   PredictionResult ──1:1── ClinicalDecision
                   (모델 산출 권고 점수)     (의사 최종 판정)

PatientProfile ──1:N── AppointmentRequest, DailyLog
Benchmark (독립 테이블, long format — 연령대×성별 기준값)
```

> `PredictionResult`(기계 산출값)와 `ClinicalDecision`(의사 판단)을 별도 테이블로 분리해,
> 모델의 결과와 의사의 최종 판단이 항상 구조적으로 구분되도록 설계했습니다.

---

## 🤖 ML 모델

5개 후보 모델(Logistic Regression / Random Forest / XGBoost / LightGBM / CatBoost)을
ROC-AUC 기준으로 비교한 결과, **Logistic Regression**을 최종 채택했습니다.

| 항목 | 내용 |
|---|---|
| 모델 | Logistic Regression |
| 입력 변수 | 26개 (신체계측, 혈압, 혈액검사, 흡연력, 기왕력 등) |
| 평가지표 | ROC-AUC 우선, Recall ≥ 0.85를 만족하는 구간에서 Precision 최대화 |
| Threshold | 0.40 |
| 결측치 처리 | train set 기준 임퓨테이션 값 고정 저장 (운영 중 재계산 금지 — 데이터 누수 방지) |
| 결측 보조 변수 | 결측률이 높은 변수는 결측 여부 자체를 별도 피처로 추가 |
| 출력 | 권고 점수(0~1) + 영향력 상위 5개 변수 기여도 |

> 검사 우선순위 선별이 목적이므로, 실제 COPD 의심군을 놓치는 False Negative를
> False Positive보다 치명적으로 보고 **Recall을 우선 기준**으로 threshold를 결정했습니다.

**기여도 계산 방식**

```
contribution = scaler.transform(X) × model.coef_
```

표준화된 입력값과 학습된 계수를 곱해 변수별 영향력을 산출하고,
절댓값 기준 상위 5개를 추려 "이번 검사에서 점수에 가장 크게 작용한 요인"으로 제공합니다.

---

## 🔬 핵심 알고리즘

| 알고리즘 | 사용 위치 | 핵심 원리 |
|---|---|---|
| 화이트리스트 기반 인증 미들웨어 | `common/middleware.py` | 화이트리스트 외 모든 경로를 기본 차단(deny-by-default)해 인증 누락을 구조적으로 방지 |
| 로지스틱 회귀 기여도 계산 | `screening/ml_model.py` | 표준화 값 × 계수로 변수별 영향력 산출, 절댓값 상위 5개 추출 |
| 정규식 멀티패턴 OCR 매칭 | `screening/services/ocr_service.py` | 항목별 복수 정규식을 순차 시도, 매칭 실패 항목만 개별 제외 |
| DB 트랜잭션 락 동시성 제어 | `appointments/views.py` | `select_for_update()`로 동일 시간대 중복 예약을 트랜잭션 단위로 차단 |
| 날짜 기반 중복 방지 | `daily_care/utils.py` | 폼 단계 1차 체크 + `unique_together` 2차 방어로 중복 체크인 차단 |
| 실시간 재추론 What-if | `screening/views.py` | 흡연 변수만 교체해 운영 모델을 그대로 재호출, 별도 근사식 없이 일관성 보장 |
| 정규화 기반 위험요인 시각화 | `benchmarks/services.py` | `(개별 기여도 / 최대 기여도) × 100`으로 단위가 다른 변수를 0~100% 막대로 통일 |

---

## ✨ 핵심 기능

**환자**
- 문진 + 검진수치 입력 (직접 입력 / 검진결과지 OCR 자동 인식)
- 폐활량검사 권고 점수 및 주요 영향 요인 확인
- 동일 연령대·성별 평균과의 비교
- 검사 결과 추적 타임라인
- What-if 시뮬레이션 (흡연 상태·흡연량 조정 시 권고 점수 변화 미리보기)
- 폐활량검사 예약, 일상 체크인
- COPD 상식 / 호흡 운동 가이드 / FAQ

**의사**
- 환자별 권고 점수 검토 및 검사 권고 여부 최종 판정
- 환자 목록 필터링 및 정렬

---

## 🚀 로컬 개발 환경 셋업

```bash
# 1. 저장소 클론
git clone <repo-url>
cd copd-prediction

# 2. 가상환경 생성 및 활성화 (Python 3.12)
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate     # macOS / Linux

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경변수 설정
cp .env.example .env
# MySQL 접속 정보, Google Cloud Vision API 인증키 경로 등을 채워주세요

# 5. 마이그레이션
python manage.py migrate

# 6. 서버 실행
python manage.py runserver
```

`http://127.0.0.1:8000/` 접속해 정상 작동을 확인합니다.

> `.env` 파일은 `.gitignore`에 등록되어 있어 git에 올라가지 않습니다.
> DB 비밀번호 등 민감정보가 포함되어 있으니 직접 공유하지 마세요.

**패키지를 새로 설치했다면**
```bash
pip freeze > requirements.txt
```

**모델(models.py)을 수정했다면**
```bash
python manage.py makemigrations
python manage.py migrate
```
새로 생성된 `migrations/000X_xxxx.py` 파일도 함께 커밋합니다.

---

## 🔄 CI/CD

`main` 브랜치 push를 트리거로 GitHub Actions가 자동 배포를 수행합니다.

```
코드 작업 → main push
      ↓
GitHub Actions (.github/workflows/deploy.yml)
      ↓
SSH 접속 → deploy.sh 실행
      ↓
git pull → pip install → migrate → collectstatic → Gunicorn 재시작
```

서버 접속 정보(IP, 계정, SSH 개인키)는 코드에 직접 작성하지 않고
GitHub Secrets에 암호화 저장해 참조합니다. 배포 스크립트는 `set -e`로 작성되어
중간 단계 실패 시 즉시 중단되며, 일부만 반영된 불완전한 배포 상태를 방지합니다.

> CD(자동 배포)는 구현되어 있으나, 자동화된 테스트·코드 검증 파이프라인(CI)은
> 별도로 구성하지 않았습니다.

---

## 🖥️ 서버 인프라

| 구성 요소 | 역할 |
|---|---|
| **Nginx** | 정적 파일 서빙, HTTPS 처리(Let's Encrypt), Reverse Proxy |
| **Gunicorn** | Django 구동 WSGI 서버 (`workers=2`, `timeout=60`) |
| **Unix Socket** | Nginx ↔ Gunicorn 통신 경로 |
| **systemd** | Gunicorn 서비스 등록, 장애 시 자동 복구 |
| **Certbot** | SSL 인증서 자동 발급 및 갱신 |

운영 환경의 메모리 제약(RAM 약 2GB)을 고려해 Gunicorn 워커 수를 2개로 제한하고
스왑 메모리를 추가해 안정화했습니다.

---

## ⚠️ 한계 및 향후 방향

**한계**
- 단일 시점 KNHANES 데이터 기반으로, 외부 코호트 검증은 미수행
- Precision이 낮아 False Positive(불필요한 검사 권고)가 발생 — Recall 우선 설계의 trade-off
- 실시간 임상 변수(증상 변화, 약물 반응 등) 미반영

**향후 방향**
- 외부 데이터셋을 통한 모델 일반화 성능 검증
- 의사용 환자 목록 화면 고도화
- CI 파이프라인(자동 테스트) 도입

---

## 🗂️ 데이터 출처

| 항목 | 내용 |
|---|---|
| 데이터 | 국민건강영양조사(KNHANES) 2024 |
| OCR | Google Cloud Vision API |
| 모델 산출물 | `copd_screening_model.pkl`, `model_config.json` |

---

## 🌿 Git 협업 흐름

```bash
git pull origin main     # 작업 전 최신 코드 반영
# 작업
git add .
git commit -m "작업 내용"
git push origin main
```

- 모든 기능 개발은 `dev` 브랜치에서 진행
- 배포가 필요할 때만 `dev` 내용을 `main`에 반영해 CI/CD 트리거
- 같은 파일 동시 수정 시 충돌 발생 가능 — 작업 전 `pull` 우선 실행