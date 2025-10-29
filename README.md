# 💰 AWS Výdajová apka (public version)

This is the **public version** of my expense tracking app connected with **Amazon AWS Bedrock** using the **Claude Haike 4.5 model** and **Streamlit** UI.

---

## 🚀 Features
- Uses **Claude Haike 4.5 (Bedrock)** for AI text generation  
- Simple and accessible **Streamlit web interface**  
- Designed for testing AWS integration (S3, Bedrock, etc.)  
- Ready for future connection with the full **Expense Tracker app**

---

## 🧠 Run locally

### 1️⃣ Clone the repo
```bash
git clone https://github.com/Deniska1980-data/aws-vydajova-apka-public.git
cd aws-vydajova-apka-public

2️⃣ Install dependencies

pip install -r requirements.txt

3️⃣ Configure AWS (once)

aws configure
(Enter your Access Key, Secret Key, and region, e.g. eu-central-1.)

4️⃣ Run the app

streamlit run app.py

☁️ AWS Bedrock setup

The app uses AWS Claude Haike 4.5 Express v1 model via Bedrock:
BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
BEDROCK_REGION = "eu-central-1"

Make sure Bedrock is enabled in your AWS account before running the app.

🧾 Requirements

Python 3.9+

boto3 >= 1.34

streamlit >= 1.37

👩‍💻 Author

Denisa Pitnerová
Public version created for AWS & AI testing – 2025
