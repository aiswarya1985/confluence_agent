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





