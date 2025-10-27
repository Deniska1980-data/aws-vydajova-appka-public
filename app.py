import os, json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import streamlit as st

# --- Konfigurácia Bedrock/Titan ---
BEDROCK_REGION = os.getenv("AWS_REGION", "eu-central-1")  # napr. eu-central-1 alebo us-east-1
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-text-express-v1")

bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

def titan_generate(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 512,
    top_p: float = 0.9,
    stop_sequences=None,
) -> str:
    """Zavolá Amazon Titan Text cez Bedrock a vráti text."""
    body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "temperature": temperature,
            "maxTokenCount": max_tokens,
            "topP": top_p,
            "stopSequences": stop_sequences or []
        }
    }
    try:
        resp = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(body),
            accept="application/json",
            contentType="application/json",
        )
        payload = json.loads(resp["body"].read())
        return payload["results"][0]["outputText"].strip()
    except (BotoCoreError, ClientError) as e:
        return f"[Bedrock error] {e}"

# --- Streamlit UI ---
st.title("💰 Výdajová apka – Amazon Titan (AWS Bedrock)")

prompt = st.text_area("Zadaj svoj text pre Titan:", "Napíš krátky popis mojej aplikácie výdavkov.")
if st.button("Generate"):
    with st.spinner("Volám Amazon Titan..."):
        result = titan_generate(prompt)
    st.write(result)
