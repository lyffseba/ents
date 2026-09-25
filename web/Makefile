.PHONY: venv install smoke run

venv:
	cd .. && python3 -m venv .venv

install: venv
	../.venv/bin/pip install -r requirements.txt httpx

smoke:
	cd .. && ENTS_DISABLE_SCHEDULER=1 SYSTEM1_BACKEND=mock GEMINI_API_KEY= OPENROUTER_API_KEY= USE_VERTEX=false .venv/bin/python scripts/test_system1.py
	cd .. && ENTS_DISABLE_SCHEDULER=1 SYSTEM1_BACKEND=mock .venv/bin/python scripts/smoke_web.py

run:
	cd .. && ENTS_DISABLE_SCHEDULER=0 .venv/bin/uvicorn web.app:app --reload --host 0.0.0.0 --port 8000
