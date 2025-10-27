import os, json, boto3
from botocore.exceptions import BotoCoreError, ClientError
import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, date as dt_date

# ============================
#   CONFIG
# ============================
st.set_page_config(page_title="Výdavková apka + Amazon Titan", layout="wide")

# --- AWS Bedrock / Titan setup ---
BEDROCK_REGION = os.getenv("AWS_REGION", "eu-central-1")  # napr. eu-central-1
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-text-express-v1")

bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

# ============================
#   TITAN FUNCTIONS
# ============================
def titan_generate(prompt: str) -> str:
    """Zavolá Amazon Titan Text cez Bedrock a vráti výstupný text."""
    body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "temperature": 0.3,
            "maxTokenCount": 512,
            "topP": 0.9,
        },
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

def titan_tab():
    st.header("🤖 Amazon Titan (AWS Bedrock)")
    st.caption("Tu si môžeš vyskúšať generovanie textu cez model Amazon Titan.")
    prompt = st.text_area("✍️ Zadaj svoj text:", "Napíš krátky popis mojej aplikácie výdavkov.")
    if st.button("Generate text"):
        with st.spinner("Volám Amazon Titan..."):
            result = titan_generate(prompt)
        st.write("**🧾 Výsledok:**")
        st.success(result)

# ============================
#   EXPENSE APP
# ============================

def expense_tab():
    # ---------------------------
    # Custom CSS for readability
    # ---------------------------
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            font-size: 16px;  
            line-height: 1.6;
        }
        h1 { font-size: 28px !important; }
        h2 { font-size: 24px !important; }
        h3 { font-size: 20px !important; }
        .stButton>button {
            font-size: 18px;
            padding: 10px 20px;
        }
        .stSelectbox>div>div {
            font-size: 16px;
        }
        </style>
        """, unsafe_allow_html=True)

    # ---------------------------
    # Language switch
    # ---------------------------
    left, right = st.columns([7, 3])
    with right:
        lang_choice = st.selectbox("🌐 Language / Jazyk", ["Slovensky / Česky", "English"], index=0)
    LANG = "sk" if "Slovensky" in lang_choice else "en"

    # ---------------------------
    # Translations
    # ---------------------------
    TEXTS = {
        "sk": {
            "app_title": "💰 Výdavkový denník / Výdajový deník",
            "subtitle": "CZK = vždy 1:1. Ostatné meny podľa denného kurzu ČNB. "
                        "Ak pre vybraný deň nie je kurz, použije sa posledný dostupný kurz.",
            "date": "📅 Dátum nákupu / Datum nákupu",
            "country": "🌍 Krajina + mena / Měna",
            "amount": "💵 Suma / Částka",
            "category": "📂 Kategória / Kategorie",
            "shop": "🏬 Obchod / miesto",
            "note": "📝 Poznámka",
            "save": "💾 Uložiť nákup",
            "list": "🧾 Zoznam nákupov",
            "summary": "📊 Súhrn mesačných výdavkov",
            "total": "Celkové výdavky",
            "rate_err": "❌ Kurz sa nepodarilo načítať.",
            "saved_ok": "Záznam uložený!",
            "rate_info": "Použitý kurz",
            "rate_from": "k",
            "export": "💾 Exportovať do CSV"
        },
        "en": {
            "app_title": "💰 Expense Diary",
            "subtitle": "CZK = always 1:1. Other currencies follow CNB daily rates.",
            "date": "📅 Purchase date",
            "country": "🌍 Country + currency",
            "amount": "💵 Amount",
            "category": "📂 Category",
            "shop": "🏬 Shop / place",
            "note": "📝 Note",
            "save": "💾 Save purchase",
            "list": "🧾 Purchase list",
            "summary": "📊 Monthly expenses summary",
            "total": "Total expenses",
            "rate_err": "❌ Could not fetch exchange rate.",
            "saved_ok": "Saved!",
            "rate_info": "Applied rate",
            "rate_from": "as of",
            "export": "💾 Export CSV"
        }
    }

    # ---------------------------
    # Categories + Countries
    # ---------------------------
    CATEGORIES = {
        "sk": ["Potraviny 🛒", "Drogérie 🧴", "Zábava 🎉", "Elektronika 💻"],
        "en": ["Groceries 🛒", "Drugstore 🧴", "Entertainment 🎉", "Electronics 💻"]
    }

    COUNTRIES = {
        "sk": ["Česko – CZK Kč", "Slovensko – EUR €", "Nemecko – EUR €"],
        "en": ["Czechia – CZK Kč", "Slovakia – EUR €", "Germany – EUR €"]
    }

    COUNTRY_TO_CODE = {}
    for label in COUNTRIES["sk"] + COUNTRIES["en"]:
        code = label.split("–")[-1].strip().split()[0]
        COUNTRY_TO_CODE[label] = code

    # ---------------------------
    # Init state
    # ---------------------------
    if "expenses" not in st.session_state:
        st.session_state["expenses"] = pd.DataFrame(columns=[
            "Date", "Country", "Currency", "Amount", "Category", "Shop", "Note",
            "Converted_CZK", "Rate_value", "Rate_date"
        ])

    # ---------------------------
    # CNB Rate Helpers
    # ---------------------------
    @st.cache_data(ttl=600)
    def fetch_cnb_txt(date_str: str):
        url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/denni_kurz.txt?date={date_str}"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.text

    def parse_rate_from_txt(txt: str, code: str):
        if not txt: return None, None, None
        lines = txt.splitlines()
        header_date = lines[0].split(" #")[0].strip() if lines else None
        for line in lines[2:]:
            parts = line.strip().split("|")
            if len(parts) == 5:
                _, _, qty, c_code, rate = parts
                if c_code == code:
                    try:
                        qty_f = float(qty.replace(",", "."))
                        rate_f = float(rate.replace(",", "."))
                        return rate_f, qty_f, header_date
                    except:
                        return None, None, header_date
        return None, None, header_date

    def get_rate_for(code: str, d: dt_date):
        d_str = d.strftime("%d.%m.%Y")
        txt = fetch_cnb_txt(d_str)
        rate, qty, header_date = parse_rate_from_txt(txt, code)
        if rate is None:
            return None, None
        return rate / qty, datetime.strptime(header_date, "%d.%m.%Y").date().isoformat()

    # ---------------------------
    # UI header
    # ---------------------------
    st.title(TEXTS[LANG]["app_title"])
    st.caption(TEXTS[LANG]["subtitle"])

    # ---------------------------
    # Input form
    # ---------------------------
    with st.form("form"):
        col1, col2 = st.columns(2)
        with col1:
            d = st.date_input(TEXTS[LANG]["date"], value=dt_date.today(), min_value=dt_date(2024,1,1))
            country = st.selectbox(TEXTS[LANG]["country"], COUNTRIES[LANG])
            category = st.selectbox(TEXTS[LANG]["category"], CATEGORIES[LANG])
        with col2:
            amount = st.number_input(TEXTS[LANG]["amount"], min_value=0.0, step=1.0)
            shop = st.text_input(TEXTS[LANG]["shop"])
            note = st.text_input(TEXTS[LANG]["note"])
        submit = st.form_submit_button(TEXTS[LANG]["save"])

    if submit:
        code = COUNTRY_TO_CODE[country]
        per_unit, rate_date = (1.0, d.isoformat()) if code == "CZK" else get_rate_for(code, d)
        if per_unit is None:
            st.error(TEXTS[LANG]["rate_err"])
        else:
            converted = round(amount * per_unit, 2)
            new_row = pd.DataFrame([{
                "Date": d.isoformat(),
                "Country": country,
                "Currency": code,
                "Amount": amount,
                "Category": category,
                "Shop": shop,
                "Note": note,
                "Converted_CZK": converted,
                "Rate_value": round(per_unit, 4),
                "Rate_date": rate_date
            }])
            st.session_state["expenses"] = pd.concat([st.session_state["expenses"], new_row], ignore_index=True)
            st.success(f"{TEXTS[LANG]['saved_ok']} {converted} CZK "
                    f"— {TEXTS[LANG]['rate_info']}: {round(per_unit,4)} CZK/1 {code} "
                    f"({TEXTS[LANG]['rate_from']} {rate_date})")

    # ---------------------------
    # List + summary
    # ---------------------------
    st.subheader(TEXTS[LANG]["list"])
    df = st.session_state["expenses"]
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.subheader(TEXTS[LANG]["summary"])
        total = df["Converted_CZK"].sum()
        st.metric(TEXTS[LANG]["total"], f"{total:.2f} CZK")

        grouped = df.groupby("Category")["Converted_CZK"].sum().reset_index()
        chart = (
            alt.Chart(grouped)
            .mark_bar()
            .encode(
                x=alt.X("Category", sort="-y", title=TEXTS[LANG]["category"]),
                y=alt.Y("Converted_CZK", title="CZK"),
                tooltip=["Category", "Converted_CZK"]
            )
            .properties(width=600, height=300)
        )
        st.altair_chart(chart, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        file_name = f"expenses_{dt_date.today().isoformat()}.csv"
        st.download_button(
            label=TEXTS[LANG]["export"],
            data=csv,
            file_name=file_name,
            mime="text/csv",
        )

# ============================
#   NAVIGATION MENU
# ============================
st.sidebar.title("🧭 Navigácia")
page = st.sidebar.radio("Vyber si stránku:", ["💰 Výdavkový denník", "🤖 Amazon Titan AI"])

if page == "💰 Výdavkový denník":
    expense_tab()
else:
    titan_tab()

