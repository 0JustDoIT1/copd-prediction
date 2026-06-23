# 🔐 SSH Key 생성 & GitHub 연결 가이드

## 1️⃣ SSH 키 생성

`ssh-keygen -t ed25519 -C "your_email@example.com"`

- 저장 경로는 기본값 사용 (Enter)
- 파일명 변경하고 싶으면 해당 경로 그대로 따라치고 마지막만 변경하면 됨
- 비밀번호는 Enter로 생략 가능 (개발용이면 보통 생략)

---

## 2️⃣ SSH 키 확인

`ls ~/.ssh`

👉 두 개 파일이 생성됨:

- id_ed25519 → 개인 키 (절대 공유 X)
- id_ed25519.pub → 공개 키 (GitHub 등록용)

---

## 3️⃣ 공개키 복사

`cat ~/.ssh/id_ed25519.pub`

👉 출력된 전체 문자열을 복사

---

## 4️⃣ GitHub 등록

GitHub에 접속 후:

Settings → SSH and GPG keys → New SSH key

- Title: 아무 이름 (예: my-laptop)
- Key: 복사한 public key 붙여넣기

---

## 5️⃣ SSH 연결 테스트

`ssh -T git@github.com`

처음 연결 시:

Are you sure you want to continue connecting? (yes/no)

👉 yes 입력

---

## ✅ 성공 메시지

Hi username! You've successfully authenticated
