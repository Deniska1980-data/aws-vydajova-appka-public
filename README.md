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


## 🧾 Requirements

Package	Version:
**Python	3.9+**
**boto3	≥ 1.34**
**streamlit	≥ 1.37**

## 👩‍💻 Author

**Denisa Pitnerová**
Developer & Cloud Automation Enthusiast
Public version created for AWS + AI integration testing — 2025
