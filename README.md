# ⚔️ 이세계 용사 마켓 (Isekai Hero Market)

> **"당신의 모험을 완성할 최강의 장비, 여기서 거래하세요."**  
> 이세계 아포칼립스 세계관을 배경으로 한 아이템 거래 웹 서비스입니다.

[![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite)](https://www.sqlite.org/)

---

## 🌐 바로가기
- **배포 주소:** [https://youngwoojeon03.pythonanywhere.com](https://youngwoojeon03.pythonanywhere.com)
- **주요 타겟:** 던전 파밍 후 아이템 처분이 곤란한 용사 및 모험가

---

## ✨ 주요 기능

### 1. 맞춤형 거래 시스템 (CRUD)
- **아이템 등록:** 상세 설명, 카테고리(무기/방어구/포션 등), 가격 설정
- **동적 검색:** 제목, 설명, 판매자 닉네임을 아우르는 통합 검색 시스템
- **조회수 및 상태 관리:** 실시간 인기 템 확인 및 판매완료 처리 기능

### 2. 보안 및 권한 관리
- **세션 기반 로그인:** 사용자별 고유 닉네임을 활용한 판매자 인증
- **작성자 보호:** 본인이 등록한 아이템만 수정 및 삭제 가능

### 3. 사이트 관리자(Admin) 기능
- **통합 대시보드:** 전체 아이템 현황 및 가입 용사 수 실시간 집계
- **질서 유지:** 부적절한 매물 강제 삭제 및 불량 유저 영구 제명 기능

---

## 🛠 기술 스택
- **Language:** Python 3
- **Web Framework:** Flask
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3 (Custom Blue Theme), Jinja2
- **Deployment:** PythonAnywhere, Git/GitHub

---

## 🗄 데이터베이스 구조

### `items` Table (아이템 정보)
| 컬럼명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `id` | INTEGER | 고유 번호 (PK) |
| `title` | TEXT | 아이템 명칭 |
| `category` | TEXT | 분류 (무기/방어구/포션 등) |
| `status` | TEXT | 판매 상태 (판매중/판매완료) |

### `users` Table (회원 정보)
| 컬럼명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `username` | TEXT | 로그인 ID (Unique) |
| `nickname` | TEXT | 서비스 활동명 |
| `date` | TEXT | 가입 일자 |

---

## 📝 개발 회고
- **성취:** Flask와 SQLite를 연동하여 실제 서비스가 가능한 웹 애플리케이션의 전체 흐름을 구현함.
- **성장:** GitHub를 통한 형상 관리 및 PythonAnywhere 배포 과정을 거치며 실무적인 개발 환경 적응력을 키움.
- **향후 계획:** 비밀번호 암호화(Werkzeug) 적용 및 RESTful API 구조로의 고도화 예정.
