# Buoi 6 - Docker, Testing, CI

## Moi truong
- OS: Windows (Docker Desktop, WSL2)
- Docker version: 29.2.1 (build a5c7197)
- Python / Node version: Python 3.14.6 / Node v24.13.1 (may local); Docker image va CI dung Python 3.12, Node 22

## Da lam
- Them `backend/Dockerfile`, `frontend/Dockerfile` (multi-stage: node build -> nginx), `frontend/nginx.conf`, `compose.yaml`, `.dockerignore`.
- Them `backend/requirements-dev.txt` (pytest), `backend/.env.docker.example`; `backend/.env.docker` tao tren may, khong commit.
- Them `backend/tests/test_openapi_contract.py` (3 test) va `pytest.ini` (pythonpath, chi lay `test_*.py`).
- Them `.github/workflows/ci.yml` (job backend, frontend, docker; docker `needs` hai job truoc). Job backend co `env: DB_*` gia vi `database.py` doc bien moi truong khi import app.
- Khong sua code nghiep vu Backend/Frontend; PostgreSQL van o tren may (host.docker.internal).

## Ket qua local
- pytest backend/tests -q: 3 passed
- npm test: 11/11 pass
- npm run build: thanh cong (35 modules)
- docker build backend / frontend: thanh cong
- docker compose up: backend healthy, frontend (Nginx) chay; mo duoc http://127.0.0.1:8080

## Mot luong tich hop da kiem tra
- Request: POST /api/enrollments {student_id: 22000004, class_section_id: WEB-01} qua http://127.0.0.1:8080; sau do DELETE /api/enrollments/22000004/WEB-01
- HTTP status: 201 (POST), 204 (DELETE)
- Log backend: request den tu 172.20.0.3 (container Nginx), khong phai tu trinh duyet
- SQL xac nhan: enrollment_events co CREATED (id 100008, 22000004, WEB-01); sau khi huy: co them event CANCELLED (id 100011, 22000004, WEB-01); event CREATED cu (100008) van con

## Debug / AI
- Loi gap phai: `docker compose up --build` bao `unable to prepare context: path "...\Tài liệu\CSDL-Web\coursehub-demo" not found`.
- Bang chung da xem: thu muc project co dau tieng Viet; `docker build` (khong qua Compose) van chay duoc voi cung duong dan; dat `COMPOSE_BAKE=false` khong doi ket qua.
- Cach xu ly: gan tag image da build thanh `coursehub-demo-backend` / `coursehub-demo-frontend` roi chay `docker compose up` (khong `--build`).
- Neu dung AI: AI goi y COMPOSE_BAKE (khong co tac dung) va cach gan tag image. Da dung cach gan tag, xac minh bang `docker compose ps` (backend healthy) va log backend co POST 201 / DELETE 204.

## Bai tap
- Bai 1: da them `test_sections_has_get_method`. Doi thu path trong test de thay CI do roi khoi phuc: job backend do o step "Test backend contract" (Missing API paths: ['/sections-sai']), frontend xanh, docker khong chay; sau git revert thi CI xanh lai
- Bai 2: loi co kiem soat (sai DB_HOST hoac sai VITE_API_BASE_URL):
  - Log/Network:
  - Cach sua:

## Pull Request / CI
- PR:
- Reviewer:
- CI run: pass/fail va nguyen nhan neu fail