## ☁️ AWS Expense App (Public Version)
**Full-Stack DevOps & Multicloud AI Agent**

This repository contains the public version of my **Expense Tracking App**. Its primary goal is to demonstrate **Multi-Cloud Orchestration** the application is hosted on **Google Cloud** and calls **Amazon AWS Bedrock** for AI logic powered by the **Claude Haiku 4.5** model.

The project was fully developed using **Streamlit**, containerized with **Docker**, and deployed to production via **Google Cloud Run**, showcasing an end-to-end cloud automation workflow.

## 🚀 Key Features & Architectural Highlights


| Category                   | Feature                                     | Description |

| **Multi-Cloud AI**     | **Claude Haiku 4.5 (Bedrock)**    | AI text generation for smart expense insights, called directly from the GCP environment. |

| **Data & Logic**       | **CNB & Calendarific APIs**       | External APIs for real-time currency exchange rates and holiday context. |

| **Frontend**           | **Streamlit UI**                  | Lightweight, fully functional bilingual (SK/CZ/EN) web interface. |

| **Containerization**   | **Docker**                        | Used to create a consistent, portable deployment artifact for Serverless PaaS. |

## 🛡️ DevSecOps & Secrets Management
A core focus was ensuring **Zero-Trust** security. All API keys and sensitive credentials are handled outside the codebase.

**Zero-Trust Principle**: No sensitive data is ever stored in this public repository.

**Secrets Manager**: AWS Access Keys (for Bedrock) and the Calendarific API Key are securely stored in **Google Secret Manager** and dynamically injected into the **Cloud Run** environment, adhering to **Least Privilege Access** standards.

**Problem Resolution**: Successfully diagnosed and resolved critical issues related to invalid AWS security tokens (*UnrecognizedClientException*) within the production environment, proving expertise in **DevSecOps troubleshooting**.

## ☁️ Production Deployment: DevOps Workflow (CI/CD)
My role in this project centered on **DevOps Engineering**, transforming code into a scalable, serverless service:

**CI/CD Pipeline**: An automated workflow (triggered via git push from Google Cloud Shell) manages the entire process.

**Cloud Build**: The *Dockerfile* is used by Cloud Build to assemble the container image.

**Deployment (Cloud Run)**: The container is deployed to **Google Cloud Run**. This serverless approach handles automatic scaling (down to zero when inactive), minimizing operational overhead.

## ⚙️ Deployment Commands
The successful production deployment was finalized using the following commands in Google Cloud Shell:

**1. Finalize and push code changes**
git add . && git commit -m "✨ FINAL: Include Dockerfile and final EB configuration."
git push

**2. Deployment command (triggers Cloud Build/Run pipeline)**
gcloud run deploy [SERVICE-NAME] --source . --region europe-west1

## 🧠 Architecture Decision Record (ADR)
**Initial Vision**: Deploy on AWS Elastic Beanstalk (EB).

**Real-World Finding**: Deployment to EB was technically successful but failed to provide public access (502 Bad Gateway / Connection Timeout) due to strict **VPC-only networking and ELB restrictions** on the underlying infrastructure.

**Final Decision: Migrate to Google Cloud Run**.

*💬 "Testing the AWS integration was a critical step. It confirmed my understanding of core cloud deployment principles (Elastic Beanstalk, EC2, S3, VPC, health checks) and my ability to **make strategic infrastructure decisions** based on real-world system behavior to ensure public service reliability."*

👩‍💻 Author
**Denisa Pitnerová** | Developer & Cloud Automation Enthusiast

Project Version: Finalized Multi-Cloud Deployment and Integration Test (10/2025) Repo: [Your GitHub Link]
