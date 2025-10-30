# 🪙 AWS Výdajová apka (Public Version)

This repository contains the public version of my **Expense Tracking App** connected to Amazon AWS Bedrock using the **Claude Haiku 4.5 model** and a **Streamlit interface**.
It serves as a proof-of-concept for AWS AI integration and multi-cloud orchestration within the byDeny Automation Framework.

---

## 🚀 Features

🤖 **Claude Haiku 4.5 (Bedrock)** — AI text generation for smart expense insights

☁️ **AWS Integration Demo** — uses Bedrock + boto3 SDK + **optional S3 storage**

💬 **Streamlit UI** — lightweight, accessible web interface for expense input

🔒 **Secrets managed via Streamlit Secrets / AWS Secrets Manager**

🧱 Ready for connection with the **full multi-agent Expense Tracker ecosystem**

---

## 🧠 Run locally

1️⃣ Clone the repo

git clone https://github.com/Deniska1980-data/aws-vydajova-apka-public.git  

cd aws-vydajova-apka-public

2️⃣ Install dependencies

pip install -r requirements.txt

3️⃣ Configure AWS (first time only)

aws configure

> Enter your Access Key, Secret Key, and Region (recommended: eu-central-1).

4️⃣ Run the app

streamlit run app.py

## ☁️ AWS Bedrock Setup

This app connects to the **Claude Haiku 4.5 Express v1** model via AWS Bedrock:

BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
BEDROCK_REGION = "eu-central-1"

✅ Ensure **Bedrock is enabled** in your AWS account before running the app.
For testing purposes, you can disable Bedrock and use dummy text generation.

## 🔐 Security Note

All API keys and credentials are **stored securely** in Streamlit Secrets or AWS Secrets Manager.
No sensitive data is ever included in this public repository.
This follows **DevSecOps** and **Least Privilege Access** principles.

## 🧾 Architecture Decision Record (ADR)

**Decision**: Migrate deployment from AWS Elastic Beanstalk → Streamlit Cloud (Google Cloud integration planned)

## 🧠 Context

During testing, the app was initially deployed on AWS Elastic Beanstalk via CloudShell (EU-Central-1).
Deployment succeeded, but the external access endpoint returned 502 Bad Gateway and ERR_CONNECTION_TIMEOUT.
Logs confirmed that the instance was healthy internally (status: Ready),
but public access was blocked due to VPC-only networking and Elastic Load Balancer restrictions.

## ⚙️ Alternatives considered

**Option	Description	Status**

AWS Elastic Beanstalk	Works internally, no external access	❌ Not compatible with Streamlit
Microsoft Azure App Service	Stable, but slower startup for Streamlit	🟡 Secondary option
Google Cloud Run	Public endpoints, auto-scaling, supports Streamlit	✅ Chosen
Streamlit Cloud	Simple, stable for small AI prototypes	✅ Used for current public version


## ✅ Decision

Migrate to Streamlit Cloud (public) with Google Cloud backup deployment planned for higher stability.
All AWS-specific secrets remain safely stored in Streamlit Secrets Manager.
The Claude Haiku 4.5 model (via AWS Bedrock) continues to be used for AI logic.

## 🚀 Result

Streamlit UI fully operational

Claude Haiku responses verified (CZ/SK/EN)

CNB & Calendarific APIs active

Secure API key handling via Streamlit Secrets

Google Cloud deployment planned for redundancy and latency improvement

---

💬 *“Testovanie AWS integrácie bolo pre mňa dôležitý krok — potvrdilo som si, že rozumiem cloudovým princípom nasadenia (Elastic Beanstalk, EC2, S3, VPC, porty, health checks) a viem sa rozhodnúť podľa reálnej infraštruktúrnej situácie.*”

## 🧾 Requirements

Package	Version:
**Python	3.9+**
**boto3	≥ 1.34**
**streamlit	≥ 1.37**

## 👩‍💻 Author

**Denisa Pitnerová**
Developer & Cloud Automation Enthusiast
Public version created for AWS + AI integration testing — 10/2025
