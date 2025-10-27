# 💰 AWS Výdajová apka (public version)

This is the **public version** of my expense tracking app connected with **Amazon AWS Bedrock** using the **Titan Text model** and **Streamlit** UI.

---

## 🚀 Features
- Uses **Amazon Titan (Bedrock)** for AI text generation  
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

The app uses Amazon Titan Text Express v1 model via Bedrock:
MODEL_ID = "amazon.titan-text-express-v1"
BEDROCK_REGION = "eu-central-1"

Make sure Bedrock is enabled in your AWS account before running the app.

🧾 Requirements

Python 3.9+

boto3 >= 1.34

streamlit >= 1.37

👩‍💻 Author

Denisa Pitnerová
Public version created for AWS & AI testing – 2025
