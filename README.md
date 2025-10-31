## ☁️ AWS Expense App (Public Version)
**Full-Stack DevOps & Multicloud AI Agent**

This repository contains the public version of my **Expense Tracking App**. Its primary goal is to demonstrate **Multi-Cloud Orchestration** the application is hosted on **Google Cloud Run (GCP)** and securely calls **Amazon AWS Bedrock** for AI logic powered by the **Claude 3 Haiku** model.

The project was fully developed using **Streamlit**, containerized with **Docker**, and deployed to production via **Google Cloud Run**, showcasing an end-to-end secure cloud automation workflow.

## 🚀 Key Features & Architectural Highlights


| Category                   | Feature                                     | Description |

| **Multi-Cloud AI**     | **Claude Haiku 4.5 (Bedrock)**    | AI text generation for smart expense insights, called directly from the GCP environment. |

| **Data & Logic**       | **CNB & Calendarific APIs**       | External APIs for real-time currency exchange rates and holiday context. |

| **Frontend**           | **Streamlit UI**                  | Lightweight, fully functional bilingual (SK/CZ/EN) web interface. |

| **Containerization**   | **Docker**                        | Used to create a consistent, portable deployment artifact for Serverless PaaS. |

## 🛡️ DevSecOps & Secrets Management

A core focus was ensuring **Zero-Trust** security. All API keys and sensitive credentials are handled outside the codebase.

**Zero-Trust Principle**: No sensitive data is stored in this public repository.

**Secrets Manager**: AWS Access Keys (for Bedrock) and the Calendarific API Key are securely stored in **Google Secret Manager** and dynamically injected into the Cloud Run environment.

🛑 Root Cause Analysis & DevOps Triumphs
The successful deployment required a deep dive into cross-platform security and environment configuration, proving advanced troubleshooting skills.

## 🛑 Root Cause Analysis & DevOps Triumphs

The successful deployment required a deep dive into cross-platform security and environment configuration, proving advanced troubleshooting skills.

| Issue Type                | Symptom/Error Message                    | Root Cause Analysis (RCA)                     | Resolution & Skill Demonstrated 

| **Authentication** | `UnrecognizedClientException` | AWS kľúče uložené v Google Secret Manageri boli poškodené (obsahovali úvodzovky/neviditeľné znaky). | 
**DevSecOps:** Vytvorenie a injektovanie **čistých hodnôt**, zabezpečenie integrity dát. |
| **GCP Permission** | `Permission denied on secret` | Servisnému účtu Cloud Run chýbala nevyhnutná IAM rola **`Secret Manager Secret Accessor`** na čítanie tajomstiev. | **IAM & Least Privilege:** Udelenie špecifickej IAM roly, vyriešenie bezpečnostného bloku na strane GCP. |
| **Environment Config** | `Unable to locate credentials` | Kód aplikácie očakával premennú **`AWS_DEFAULT_REGION`**, zatiaľ čo prostredie poskytovalo len `AWS_REGION`. | **Troubleshooting:** Zarovnanie názvu premennej v Cloud Run tak, aby **presne zodpovedal kódu**, dosiahnutie úspešnej komunikácie. |

## ☁️ Production Deployment: DevOps Workflow (CI/CD)
The successful production deployment was finalized using the following command in Google Cloud Shell:

gcloud run deploy vydajova-appka-gcp --source . --region europe-west1

**CI/CD Pipeline**: An automated workflow (triggered via git push from Google Cloud Shell) manages the entire process.

**Cloud Build**: The *Dockerfile* is used by Cloud Build to assemble the container image.

**Deployment (Cloud Run)**: The container is deployed to **Google Cloud Run**. This serverless approach handles automatic scaling (down to zero when inactive), minimizing operational overhead.

## ⚙️ Deployment Commands
The successful production deployment was finalized using the following commands in Google Cloud Shell:

**1. Finalize and push code changes**

git add . 

git commit -m "✨ FINAL DEVOPS SUCCESS: Resolved AWS authentication and IAM permissions across GCP/AWS for stable multi-cloud operation."

git push

**2. Deployment command (triggers Cloud Build/Run pipeline)**

gcloud run deploy [SERVICE-NAME] --source . --region europe-west1

## 🧠 Architecture Decision Record (ADR)
**Initial Vision**: Deploy on AWS Elastic Beanstalk (EB).

**Real-World Finding**: Deployment to EB was technically successful but failed to provide public access (502 Bad Gateway / Connection Timeout) due to strict **VPC-only networking and ELB restrictions** on the underlying infrastructure.

**Final Decision: Migrate to Google Cloud Run**.

*💬 "Testing the AWS integration was a critical step. It confirmed my understanding of core cloud deployment principles (Elastic Beanstalk, EC2, S3, VPC, health checks) and my ability to **make strategic infrastructure decisions** based on real-world system behavior to ensure public service reliability."*

## 🌍 Application Status
The application is now fully stable and serving requests, proving the viability of the multi-cloud architecture.

👩‍💻 Author
**Denisa Pitnerová** | Developer & Cloud Automation Enthusiast

Project Version: Finalized Multi-Cloud Deployment and Integration Test (10/2025) Repo: [Your GitHub Link]
