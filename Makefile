.PHONY: dev

dev:
	python -m uvicorn qrparser.web.main:app --reload --reload-dir src --reload-dir tests