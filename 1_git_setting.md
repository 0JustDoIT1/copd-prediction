# 📦 Git 협업 초기 세팅 가이드 (신규 팀원용)

새로운 팀원이 레포지토리에 참여할 때 필요한 **전체 세팅 순서**를 정리합니다.

---

## 🚀 전체 흐름

```bash
Git 설치 → 사용자 설정 → SSH 키 생성 → SSH 등록 → (레포 권한 추가) → clone → 작업
```

---

## 1️⃣ Git 설치

각자 로컬 PC에 Git 설치

---

## 2️⃣ 사용자 정보 설정 (필수 ❗)

```bash
git config --global user.name "본인 이름"
git config --global user.email "본인 이메일"
```

👉 커밋 작성자 정보 설정 (안 하면 기록 꼬임)

---

## 3️⃣ SSH 키 생성

```bash
ssh-keygen -t ed25519 -C "본인 이메일"
```

👉 엔터 계속 눌러서 생성

---

## 4️⃣ GitHub에 SSH 키 등록

1. 아래 파일 열기

```
~/.ssh/id_ed25519.pub
```

2. 내용 복사

3. GitHub
   → Settings
   → SSH and GPG keys
   → New SSH key 등록

---

## 5️⃣ 레포지토리 협업 권한 추가 (레포 만든 사람)

👉 레포 생성자가 진행

- GitHub → Settings → Collaborators
- 팀원 GitHub ID 추가

⚠️ 이 과정 없으면 push 불가능

---

## 6️⃣ 레포지토리 클론

```bash
git clone git@github.com:레포주소.git
```
