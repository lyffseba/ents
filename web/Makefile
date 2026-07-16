.PHONY: venv install smoke run

venv:
	cd .. && python3 -m venv .venv

install: venv
	../.venv/bin/pip install -r requirements.txt httpx

smoke:
	cd .. && ENTS_DISABLE_SCHEDULER=1 .venv/bin/python scripts/smoke_web.py

run:
	cd .. && ENTS_DISABLE_SCHEDULER=0 .venv/bin/uvicorn web.app:app --reload --host 0.0.0.0 --port 8000
