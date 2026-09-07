@echo off
cd backend
python -m pip install -r requirements.txt
set PYTHONPATH=.
uvicorn app.main:app --reload
