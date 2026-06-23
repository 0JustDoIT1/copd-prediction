# 📦 R 프로젝트 Git 협업 기본 흐름 정리

팀원들과 R 파일을 공유하기 위한 **기본 Git 작업 흐름**을 간단하게 정리합니다.

---

## 🔁 기본 작업 순서 (매우 중요)

```bash
git pull → 작업 → git add → git commit → git push
```

---

## 1️⃣ 최신 코드 가져오기 (pull)

작업 시작 전 **항상 먼저 실행**

```bash
git pull origin main
```

👉 다른 팀원이 작업한 내용을 내 로컬에 반영

---

## 2️⃣ 작업 진행

- `.R`, `.Rmd`, 데이터 파일 등 수정
- 분석 코드 작성 / 수정

---

## 3️⃣ 변경 파일 스테이징 (add)

```bash
git add .
```

또는 특정 파일만:

```bash
git add 파일명.R
```

---

## 4️⃣ 커밋 (commit)

```bash
git commit -m "작업 내용 간단히 설명"
```

예시:

```bash
git commit -m "회귀분석 코드 추가 및 전처리 수정"
```

---

## 5️⃣ 원격 저장소로 업로드 (push)

```bash
git push origin main
```

👉 팀원들이 볼 수 있도록 코드 업로드 완료

---

## ⚠️ 협업 시 주의사항

### ✔️ pull 먼저!

- 항상 작업 전에 `git pull`
- 충돌(conflict) 방지

### ✔️ 커밋 메시지 명확하게

- 무엇을 했는지 간단히 작성

### ✔️ 자주 push

- 작업 쌓아두지 말고 중간중간 공유

### ✔️ 충돌 발생 시

- 같은 파일을 동시에 수정하면 발생
- 충돌 부분 확인 후 수정 → 다시 commit

---

## 💡 추천 루틴

```bash
git pull origin main
# 작업
git add .
git commit -m "작업 내용"
git push origin main
```

---

## 🚀 한 줄 요약

👉 **"작업 전에 pull, 작업 후 add → commit → push"**

---
