# CourseHub

React + FastAPI + PostgreSQL (database chay tren may, khong dong goi trong Docker).

## Chay kieu phat trien (Buoi 5)
```
# Terminal 1 (thu muc goc)
python -m uvicorn backend.app.main:app --reload
# Terminal 2
cd frontend
npm install
npm run dev        # http://127.0.0.1:5173/
```

## Chay bang Docker Compose (Buoi 6)
```
copy backend\.env.docker.example backend\.env.docker   # macOS/Linux: cp
# sua DB_USER, DB_PASSWORD giong backend/.env; DB_HOST giu host.docker.internal
docker compose up --build
```
- Giao dien: http://127.0.0.1:8080 (Nginx chuyen /api -> backend:8000)
- API truc tiep: http://127.0.0.1:8000/docs
- Dung: `docker compose down`

## Kiem thu
```
python -m pip install -r backend/requirements-dev.txt
pytest backend/tests -q
cd frontend && npm ci && npm test && npm run build
```
