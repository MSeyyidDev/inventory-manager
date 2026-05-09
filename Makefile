.PHONY: install seed dev-backend dev-frontend test test-backend test-frontend clean

install:
	cd backend && python -m pip install -r requirements.txt
	cd frontend && npm install

seed:
	cd backend && python -m app.seed

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	cd backend && pytest -q

test-frontend:
	cd frontend && npm test -- --run

clean:
	rm -rf backend/.pytest_cache backend/__pycache__ backend/inventory.db
	rm -rf frontend/node_modules frontend/dist
