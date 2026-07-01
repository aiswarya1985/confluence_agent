Project name
confluenceagent
Project number
17897045860
Project ID
confluenceagent


# RAG Scale Test: Execution & Deployment Guide

This guide provides the necessary commands to set up, run locally, and deploy the Enterprise Agentic RAG application to Google Cloud Platform.

---

## 🛠️ Useful Helper Commands
Use these commands to quickly find project details or check your status:

```powershell
# Get your Project Number (needed for Service Accounts)
gcloud projects describe confluenceagent --format="value(projectNumber)"

# See which account is currently logged in
gcloud auth list

# See all current configuration (Project ID, Region, Account)
gcloud config list

# set the newly created project
gcloud config set project confluenceagent

# if warning give the below command
gcloud auth application-default set-quota-project confluenceagent

# List all enabled APIs in this project
gcloud services list --enabled

# List all VPC connectors in a region
gcloud compute networks vpc-access connectors list --region us-central1
```

---

## 1. Google Cloud Initial Setup (Terminal)
Before running any cloud-related commands, ensure you have the `gcloud` CLI installed and authenticated.

### Authentication & Project Configuration
```powershell
# Login to Google Cloud
gcloud auth login

# Login for Application Default Credentials (needed for local python scripts)
gcloud auth application-default login

# Set the active project
gcloud config set project confluenceagent

# Enable required Google Cloud Services
gcloud services enable \
    artifactregistry.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    sqladmin.googleapis.com \
    documentai.googleapis.com \
    compute.googleapis.com \
    discoveryengine.googleapis.com

# Create GCS Buckets (if they don't exist)- not needed for this project
gcloud storage buckets create gs://dmtxpress-rag-raw --location=us-central1
gcloud storage buckets create gs://dmtxpress-rag-processed --location=us-central1
```

### IAM Permissions (Roles)
Run these to ensure your account has the necessary permissions:
```powershell
gcloud projects add-iam-policy-binding confluenceagent \
    --member="user:cuteaisw@gmail.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding confluenceagent \
    --member="user:cuteaisw@gmail.com" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding confluenceagent \
    --member="user:cuteaisw@gmail.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding confluenceagent \
    --member="user:cuteaisw@gmail.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding confluenceagent \
    --member="user:cuteaisw@gmail.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding confluenceagent \
    --member="user:cuteaisw@gmail.com" \
    --role="roles/documentai.apiUser"

gcloud projects add-iam-policy-binding confluenceagent \
    --member="user:cuteaisw@gmail.com" \
    --role="roles/discoveryengine.editor"

# Grant Document AI access to the Cloud Run Service Account
gcloud projects add-iam-policy-binding confluenceagent \
    --member="serviceAccount:17897045860-compute@developer.gserviceaccount.com" \
    --role="roles/documentai.apiUser"

# Grant VPC access to the Cloud Run Service Agent
gcloud projects add-iam-policy-binding confluenceagent \
    --member="serviceAccount:service-17897045860@serverless-robot-prod.iam.gserviceaccount.com" \
    --role="roles/vpcaccess.user"

# Grant permission to the Cloud Run Service Account (Production)
gcloud projects add-iam-policy-binding confluenceagent \
    --member="serviceAccount:17897045860-compute@developer.gserviceaccount.com" \
    --role="roles/discoveryengine.editor"
```

---

## 2. Local Environment Setup

### Virtual Environment & Dependencies
```powershell
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables (.env)
---

## 3. Data Ingestion
The ingestion pipeline is now **Universal**. It scans the `DATA/` directory, automatically identifies "true" and "noisy" subfolders, parses PDF/HTML/TXT, and syncs everything to GCP.



---

## 4. Running Locally

### Start the FastAPI Backend
```powershell
uvicorn app.main:app --reload --port 8000
```

### Start the Streamlit UI
```powershell
streamlit run ui/app.py
```

---

## 5. Build and Push Image (No Local Docker Required)
Use Google Cloud Build to build the container image in the cloud and push it directly to Artifact Registry.

### Create Repository
```powershell
# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create confluenceagent \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for RAG API"
```

### Build and Push using Cloud Build
```powershell
# Submit a build to Google Cloud Build (this builds the image in the cloud and pushes it)
# change to docker directory first
gcloud builds submit --tag us-central1-docker.pkg.dev/confluenceagent/confluenceagent/confluenceagent-api:v1 "$(pwd)"
```

### if error run this

gcloud projects add-iam-policy-binding confluenceagent \
    --member="serviceAccount:17897045860-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
	
gcloud projects add-iam-policy-binding confluenceagent \
    --member="serviceAccount:17897045860-compute@developer.gserviceaccount.com" \
    --role="roles/logging.logWriter"	
	
### as the docker file is in in docker folder the below will not run
	
gcloud builds submit --tag us-central1-docker.pkg.dev/confluenceagent/confluenceagent/confluenceagent-api:v1 "$(pwd)"

create cloudbuild.yaml

run gcloud builds submit --config cloudbuild.yaml .
	
	

### 6. Create a vpc connector:

Note that underscores (_) are not allowed in VPC connector names. You must use a hyphen (-) instead.

```
gcloud compute networks vpc-access connectors create confleuncevps \
    --region us-central1 \
    --network default \
    --range 10.8.0.0/28

```

Check vpc networks
```
gcloud compute networks vpc-access connectors list --region us-central1

```

---

## 7. Cloud Run Deployment
Deploy the containerized app to Google Cloud Run.

####we need to set env variables also but for github checkin not allowed

```powershell

gcloud run deploy rag-api \
  --image us-central1-docker.pkg.dev/confluenceagent/confluenceagent/confluenceagent-api:v1 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout=300 \
  --vpc-connector confleuncevps \
  
    

```


### steps to paste in gitbash without error
remove \ by replacing
open gitbash and paste

