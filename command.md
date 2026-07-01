## How to install UV
uv init
## choose the python version
uv venv confluence_agent --python 3.11.13
## activate python environment
confluence_agent\Scripts\Activate.ps1
## if error

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

## activate again
confluence_agent\Scripts\Activate.ps1

### how to initialize git and push to github
git init

git add README.md

git commit -m "first commit"

git branch -M main

git remote add origin https://github.com/aiswarya1985/confluence_agent.git

git push -u origin main


### to install requirements

uv pip install -r requirements.txt

### to push all files that has changed
git add .

### commit with relevant message

git commit -m "first commit"

### push
git push

### configure logfire

create a project in logfire
create a write token 
uv pip install logfire
python -m logfire auth
python -m logfire projects use ## link the project
.logfire will be created

do logfire.configure to use in project

## to convert to packages

uv pip install -e .

### run seperate files

change to the directory where file is loacted

### just for ingestion testing
uv run --active confluence_loader.py

## 4. Running Locally

### Start the FastAPI Backend
```powershell
uvicorn app.main:app --reload --port 8000
```

### Start the Streamlit UI
```powershell
streamlit run ui/app.py
```










