# app.py  — Expense Diary (AWS/Claude Haiku 4.5 - ready, voliteľný Claude), CNB TXT + Calendarific + IssueCoin

from datetime import datetime, date as dt_date
from random import choice, random

import pandas as pd
import requests
import altair as alt

import os
import json
import boto3
import streamlit as st

# ------------------------------------------------------------
# Inicializácia AWS Bedrock klienta
# ------------------------------------------------------------
def get_bedrock_client():
    try:
        client = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_DEFAULT_REGION", "eu-central-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        return client
    except Exception as e:
        st.warning(f"⚠️ Bedrock klient sa nepodarilo inicializovať: {e}")
        return None


# ------------------------------------------------------------
# Funkcia na volanie Claude Haiku 4.5 (opravená verzia)
# ------------------------------------------------------------
def claude_haiku_45_init(ctx):
    try:
        client = get_bedrock_client()
        if client is None:
            return "Bedrock klient nie je dostupný."

        model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

        # 👇 Dôležitá zmena: používame `prompt` namiesto `inputText`
        body = {
            "prompt": f"Napíš krátku, priateľskú hlášku podľa týchto údajov: {ctx}",
            "max_tokens_to_sample": 200,
            "temperature": 0.7,
            "anthropic_version": "bedrock-2023-05-31"
        }

        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )

        result = json.loads(response["body"].read())
        output_text = result.get("completion", "").strip()

        return output_text if output_text else "Claude Haiku 4.5 nevrátil žiadny text."

    except Exception as e:
        return f"⚠️ Claude Haiku 4.5 sa odmietol: {e}"

# ---------------------------
# Page & basic styling
# ---------------------------
st.set_page_config(page_title="💰 Výdavkový denník / Expense Diary (Claude Haiku 4.5-ready)", layout="wide")
st.markdown("""
<style>
    html, body, [class*="css"] { font-size: 16px; line-height: 1.6; }
    h1 { font-size: 28px !important; } h2 { font-size: 24px !important; } h3 { font-size: 20px !important; }
    .stButton>button { font-size: 18px; padding: 10px 20px; }
    .stSelectbox>div>div { font-size: 16px; }
    /* language switch holder (top-right) */
    .lang-slot { position: relative; height: 0; }
    .lang-slot > div { position: absolute; right: 0; top: -64px; width: 260px; }
    /* badges for debug panel */
    .badge-ok {background:#16a34a; color:white; padding:2px 8px; border-radius:999px; font-size:12px;}
    .badge-err {background:#dc2626; color:white; padding:2px 8px; border-radius:999px; font-size:12px;}
    .badge-off {background:#6b7280; color:white; padding:2px 8px; border-radius:999px; font-size:12px;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar – Settings / Debug
# ---------------------------
with st.sidebar:
    st.header("⚙️ Nastavenia / Settings")
    show_debug = st.checkbox("Zobraziť debug panel", value=False)
    # Calendarific API key – zobraz len ak chýba v ENV
    _env_key = os.getenv("CALENDARIFIC_API_KEY", "").strip()
    if not _env_key:
        user_key = st.text_input("🔑 Calendarific API key (ak chýba v ENV)", type="password")
        if user_key:
            st.session_state["CALENDARIFIC_API_KEY"] = user_key.strip()
            st.success("API key uložený do session (platí do refreshu).")
    else:
        st.caption("Calendarific key nájdený v ENV (CALENDARIFIC_API_KEY).")
    st.markdown("---")
    st.caption("🧠 Claude Haiku 4.5 je voliteľný. Ak nie je aktivovaný v ENV, appka beží s IssueCoin hláškami.")

# Debug store
if "DEBUG" not in st.session_state:
    st.session_state.DEBUG = {"cnb": {"ok": None, "msg": "", "ts": None},
                              "calendarific": {"ok": None, "msg": "", "ts": None},
                              "Claude Haiku 4.5": {"ok": None, "msg": "", "ts": None, "last_hint": None}}

def _debug_set(section: str, ok: bool|None, msg: str, extra=None):
    st.session_state.DEBUG[section]["ok"] = ok
    st.session_state.DEBUG[section]["msg"] = msg
    st.session_state.DEBUG[section]["ts"] = datetime.now().strftime("%H:%M:%S")
    if section == "titan" and extra is not None:
        st.session_state.DEBUG[section]["last_hint"] = extra

# ---------------------------
# Language selector (top-right)
# ---------------------------
lang_slot = st.container()
with lang_slot:
    st.markdown('<div class="lang-slot"></div>', unsafe_allow_html=True)
lang_placeholder = st.empty()
with lang_placeholder.container():
    col_lang = st.columns([8, 2])[1]
    with col_lang:
        lang_choice = st.selectbox("🌐 Jazyk / Language", ["Slovensky / Česky", "English"], index=0)
LANG = "sk" if "Slovensky" in lang_choice else "en"

# ---------------------------
# Texts
# ---------------------------
TEXTS = {
    "sk": {
        "app_title": "💰 Výdavkový denník / Výdajový deník",
        "subtitle": ("CZK = vždy 1:1. Ostatné meny podľa denného kurzu ČNB (TXT feed). "
                     "Ak pre vybraný deň nie je kurz, použije sa posledný dostupný kurz. "
                     "Sviatky cez Calendarific (API kľúč z ENV alebo session). "
                     "Claude Haiku 4.5 hlášky sa objavia až po aktivácii."),
        "date": "📅 Dátum nákupu / Datum nákupu",
        "country": "🌍 Krajina + mena / Měna",
        "amount": "💵 Suma / Částka",
        "category": "📂 Kategória / Kategorie",
        "shop": "🏬 Obchod / miesto",
        "note": "📝 Poznámka",
        "save": "💾 Uložiť nákup / Uložit nákup",
        "list": "🧾 Zoznam nákupov / Seznam nákupů",
        "summary": "📊 Súhrn mesačných výdavkov / Souhrn měsíčních výdajů",
        "total": "Celkové výdavky / Celkové výdaje",
        "rate_err": "❌ Kurz sa nepodarilo načítať (CNB TXT).",
        "saved_ok": "Záznam uložený!",
        "rate_info": "Použitý kurz",
        "rate_from": "k",
        "export": "💾 Exportovať do CSV",
        "holiday_msg": "🎌 Dnes je štátny sviatok ({name}) – uži deň s rozumom!",
        "issuecoin_title": "🤖 IssueCoin hovorí",
        "claude_haiku_off": "🧠 Claude Haiku 4.5 vypnutý – používam vlastné (RAG) hlášky.",
    },
    "en": {
        "app_title": "💰 Expense Diary",
        "subtitle": ("CZK = always 1:1. Other currencies follow CNB daily TXT feed. "
                     "If missing for the date, the latest available rate is used. "
                     "Holidays via Calendarific (ENV or session key). "
                     "Claude Haiku 4.5 messages will appear once enabled."),
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
        "rate_err": "❌ Could not fetch exchange rate (CNB TXT).",
        "saved_ok": "Saved!",
        "rate_info": "Applied rate",
        "rate_from": "as of",
        "export": "💾 Export CSV",
        "holiday_msg": "🎌 Today is a public holiday ({name}) – enjoy wisely!",
        "issuecoin_title": "🤖 IssueCoin says",
        "claude_haike_off": "🧠 Claude Haike 4.5 disabled – using built-in RAG messages.",
    }
}

# ---------------------------
# Categories
# ---------------------------
CATEGORIES = {
    "sk": [
        "Potraviny 🛒 / Potraviny 🛒","Drogérie 🧴 / Drogérie 🧴","Doprava 🚌 / Doprava 🚌",
        "Reštaurácie a bary 🍽️ / Restaurace a bary 🍽️","Zábava 🎉 / Zábava 🎉","Odevy 👕 / Oblečení 👕",
        "Obuv 👟 / Obuv 👟","Elektronika 💻 / Elektronika 💻","Domácnosť / nábytok 🛋️ / Domácnost / nábytek 🛋️",
        "Šport a voľný čas 🏀 / Sport a volný čas 🏀","Zdravie a lekáreň 💊 / Zdraví a lékárna 💊",
        "Cestovanie / dovolenka ✈️ / Cestování / dovolená ✈️","Vzdelávanie / kurzy 📚 / Vzdělávání / kurzy 📚"
    ],
    "en": [
        "Groceries 🛒","Drugstore 🧴","Transport 🚌","Restaurants & Bars 🍽️","Entertainment 🎉",
        "Clothing 👕","Shoes 👟","Electronics 💻","Household / Furniture 🛋️","Sports & Leisure 🏀",
        "Health & Pharmacy 💊","Travel / Holiday ✈️","Education / Courses 📚"
    ]
}

# ---------------------------
# Country / currency list (full)
# ---------------------------
COUNTRIES = {
    "sk": [
        "Česko – CZK Kč","Slovensko – EUR €","Nemecko – EUR € / Německo – EUR €","Rakúsko – EUR € / Rakousko – EUR €",
        "Francúzsko – EUR € / Francie – EUR €","Španielsko – EUR € / Španělsko – EUR €","Taliansko – EUR € / Itálie – EUR €",
        "Holandsko – EUR € / Nizozemsko – EUR €","Belgicko – EUR € / Belgie – EUR €","Fínsko – EUR € / Finsko – EUR €",
        "Írsko – EUR € / Irsko – EUR €","Portugalsko – EUR €","Grécko – EUR € / Řecko – EUR €","Slovinsko – EUR €",
        "Litva – EUR €","Lotyšsko – EUR €","Estónsko – EUR €","Malta – EUR €","Cyprus – EUR €",
        "Chorvátsko – EUR € / Chorvatsko – EUR €","USA – USD $","Veľká Británia – GBP £ / Velká Británie – GBP £",
        "Poľsko – PLN zł / Polsko – PLN zł","Maďarsko – HUF Ft / Maďarsko – HUF Ft","Švajčiarsko – CHF ₣ / Švýcarsko – CHF ₣",
        "Dánsko – DKK kr / Dánsko – DKK kr","Švédsko – SEK kr / Švédsko – SEK kr","Nórsko – NOK kr / Norsko – NOK kr",
        "Kanada – CAD $","Japonsko – JPY ¥"
    ],
    "en": [
        "Czechia – CZK Kč","Slovakia – EUR €","Germany – EUR €","Austria – EUR €","France – EUR €","Spain – EUR €",
        "Italy – EUR €","Netherlands – EUR €","Belgium – EUR €","Finland – EUR €","Ireland – EUR €","Portugal – EUR €",
        "Greece – EUR €","Slovenia – EUR €","Lithuania – EUR €","Latvia – EUR €","Estonia – EUR €","Malta – EUR €",
        "Cyprus – EUR €","Croatia – EUR €","USA – USD $","United Kingdom – GBP £","Poland – PLN zł","Hungary – HUF Ft",
        "Switzerland – CHF ₣","Denmark – DKK kr","Sweden – SEK kr","Norway – NOK kr","Canada – CAD $","Japan – JPY ¥"
    ]
}
COUNTRY_TO_CODE = {label: label.split("–")[-1].strip().split()[0] for label in (COUNTRIES["sk"] + COUNTRIES["en"])}

# ---------------------------
# State init
# ---------------------------
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(columns=[
        "Date","Country","Currency","Amount","Category","Shop","Note","Converted_CZK","Rate_value","Rate_date"
    ])

# ---------------------------
# CNB TXT feed helpers
# ---------------------------
@st.cache_data(ttl=600)
def fetch_cnb_txt(date_str: str):
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={date_str}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            _debug_set("cnb", False, f"HTTP {r.status_code} @ date={date_str}")
            return None
        return r.text
    except Exception as e:
        _debug_set("cnb", False, f"Exception: {e}")
        return None

@st.cache_data(ttl=600)
def fetch_cnb_txt_latest():
    url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            _debug_set("cnb", False, f"HTTP {r.status_code} @ latest")
            return None
        return r.text
    except Exception as e:
        _debug_set("cnb", False, f"Exception latest: {e}")
        return None

def parse_rate_from_txt(txt: str, code: str):
    if not txt:
        return None, None, None
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
                except Exception:
                    return None, None, header_date
    return None, None, header_date

def get_rate_for(code: str, d: dt_date):
    if code == "CZK":
        _debug_set("cnb", True, "CZK=1 (no fetch)")
        return 1.0, d.isoformat()
    d_str = d.strftime("%d.%m.%Y")
    txt = fetch_cnb_txt(d_str)
    rate, qty, header_date = parse_rate_from_txt(txt, code)
    if rate is None:
        txt2 = fetch_cnb_txt_latest()
        rate, qty, header_date = parse_rate_from_txt(txt2, code)
        rate_date_iso = datetime.today().date().isoformat()
        if rate is None:
            _debug_set("cnb", False, f"No rate for {code} (date & latest)")
            return None, None
        _debug_set("cnb", True, f"Used latest for {code}")
    else:
        try:
            rate_date_iso = datetime.strptime(header_date, "%d.%m.%Y").date().isoformat()
        except Exception:
            rate_date_iso = d.isoformat()
        _debug_set("cnb", True, f"Used daily for {code}")
    return rate/qty, rate_date_iso

# ---------------------------
# Calendarific (ENV or session key)
# ---------------------------
def _calendarific_key() -> str:
    if os.getenv("CALENDARIFIC_API_KEY", "").strip():
        return os.getenv("CALENDARIFIC_API_KEY").strip()
    return st.session_state.get("CALENDARIFIC_API_KEY", "")

@st.cache_data(ttl=3600)
def calendarific_holidays(api_key: str, country_code: str, year: int, month: int, day: int):
    if not api_key:
        _debug_set("calendarific", None, "No API key (ENV/session)")
        return []
    url = ( "https://calendarific.com/api/v2/holidays"
            f"?api_key={api_key}&country={country_code}&year={year}&month={month}&day={day}" )
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            _debug_set("calendarific", False, f"HTTP {r.status_code}")
            return []
        data = r.json()
        hols = data.get("response", {}).get("holidays", [])
        _debug_set("calendarific", True, f"{len(holidays:=hols)} holiday(s)")
        return hols
    except Exception as e:
        _debug_set("calendarific", False, f"Exception: {e}")
        return []

def resolve_country_for_calendarific(country_label: str):
    if "Česko" in country_label or "Czech" in country_label:
        return "CZ"
    if "Slovensko" in country_label or "Slovakia" in country_label:
        return "SK"
    return "CZ"

# ---------------------------
# IssueCoin – seasonal & fun messages (RAG-like static logic)
# ---------------------------
SEASONAL_PACK = {
    "spring": {
        "emoji": "🌷🧘‍♀️🌱💐🥚",
        "lines_sk": [
            "Jar je tu! 💐 Dýchni zhlboka a míňaj s rozumom.",
            "Cvičíme a šetríme – dvojitý zisk! 🧘‍♀️",
            "Záhradka rastie, rozpočet nech neklesá. 🌱"
        ],
        "lines_en": [
            "Spring vibes! 💐 Spend smart, breathe easy.",
            "Move your body, not your budget. 🧘‍♀️",
            "Let the garden grow, not the expenses. 🌱"
        ]
    },
    "summer": {
        "emoji": "☀️😎🏖️🍉",
        "lines_sk": [
            "Leto volá! ☀️ Slnečné okuliare a rozumné nákupy.",
            "More, dovolenka, prázdniny – s mierou. 😎",
            "Melón áno, mínus nie. 🍉"
        ],
        "lines_en": [
            "Summer time! ☀️ Shades on, costs down.",
            "Beach, holidays, sunshine – keep it balanced. 😎",
            "Yes to watermelon, no to overspend. 🍉"
        ]
    },
    "autumn": {
        "emoji": "🍂🍄🧺🫐",
        "lines_sk": [
            "Jeseň prichádza 🍂 – košík húb áno, dlh nie.",
            "Čučoriedky sladké, účet nech nie. 🫐",
            "Viac dažďa, menej impulzov. ☔"
        ],
        "lines_en": [
            "Autumn mode 🍂 – mushrooms in basket, debt out.",
            "Blueberries sweet, bills not. 🫐",
            "More rain, fewer impulses. ☔"
        ]
    },
    "winter": {
        "emoji": "❄️🧣☃️🎄",
        "lines_sk": [
            "Zima je tu ❄️ – šál zahreje, rozpočet šetrí.",
            "Hrnček teplý, nákupy pokojné. ☕",
            "Sneh vonku, pohoda doma. ☃️"
        ],
        "lines_en": [
            "Winter is here ❄️ – scarf on, spending calm.",
            "Warm mug, cool head. ☕",
            "Snow outside, peace inside. ☃️"
        ]
    },
    "xmas": {
        "emoji": "🎄✨🎁",
        "lines_sk": [
            "Vianočná pohoda 🎄 – 10.–26.12. spomaľ a uži si blízkych.",
            "Darček s láskou, nie s nervami. 🎁",
            "Kľudné sviatky a rozumná peňaženka. ✨"
        ],
        "lines_en": [
            "Christmas calm 🎄 – Dec 10–26, slow down & enjoy.",
            "Gifts with love, not stress. 🎁",
            "Peaceful holidays, mindful wallet. ✨"
        ]
    },
    "easter": {
        "emoji": "🐣🌼🥚",
        "lines_sk": [
            "Veľká noc prichádza 🐣 – chvíľa pokoja a pohody.",
            "Vajíčko áno, prázdny účet nie. 🥚",
            "Jar + sviatky = oddych a mierne nákupy. 🌼"
        ],
        "lines_en": [
            "Easter time 🐣 – peace and balance.",
            "Eggs yes, empty wallet no. 🥚",
            "Spring + holiday = rest & mindful spend. 🌼"
        ]
    }
}

GENERAL_QUOTES = {
    "sk": ["💡 Ušetri dnes, potešíš sa zajtra.",
           "💸 Aj drobné sa rátajú – špeciálne v piatok. 😉",
           "🛒 Tvoj košík je plný, verím, že aj s rozumom!",
           "😅 Ceny rastú, ale tvoj prehľad tiež."],
    "en": ["💡 Save today, smile tomorrow.",
           "💸 Every coin counts – especially on Fridays. 😉",
           "🛒 Full cart, calm mind!",
           "😅 Prices rise, but so does your awareness."]
}

def current_season(dt: dt_date) -> str:
    m = dt.month
    if m in (12, 1, 2): return "winter"
    if m in (3, 4, 5):  return "spring"
    if m in (6, 7, 8):  return "summer"
    return "autumn"

def seasonal_message(d: dt_date, lang="sk") -> str:
    pack = SEASONAL_PACK["xmas"] if (d.month == 12 and 10 <= d.day <= 26) else SEASONAL_PACK[current_season(d)]
    line = choice(pack["lines_sk"] if lang == "sk" else pack["lines_en"])
    return f"{pack['emoji']} {line}"

def holiday_message(holidays: list, lang="sk") -> str | None:
    if not holidays:
        return None
    names = [h.get("name", "") for h in holidays]
    names_lc = " | ".join(names).lower()
    if any(k in names_lc for k in ["easter", "velikonoce", "veľká noc"]):
        pack = SEASONAL_PACK["easter"]
        line = choice(pack["lines_sk"] if lang == "sk" else pack["lines_en"])
        return f"{pack['emoji']} {line}"
    shown = holidays[0].get("name", "Holiday")
    msg = TEXTS[lang]["holiday_msg"].format(name=shown)
    return f"🎉 {msg}"

def issuecoin_block_show(d: dt_date, holidays: list, lang="sk"):
    st.markdown(f"**{TEXTS[lang]['issuecoin_title']}**")
    st.info(seasonal_message(d, lang))
    if random() < 0.5:
        st.success(choice(GENERAL_QUOTES[lang]))
    hm = holiday_message(holidays, lang)
    if hm:
        st.warning(hm)

# ---------------------------------------------
# Claude Haiku 4.5 (optional; safe no-op when disabled)
# ---------------------------------------------

def claude_haiku_enabled() -> bool:
    return os.getenv("ENABLE_CLAUDE_HAIKU", "0") == "1" and bool(os.getenv("BEDROCK_API_KEY"))

def claude_haiku_hint(context: dict) -> str | None:
    if not claude_haiku_enabled():
        _debug_set("Claude Haiku 4.5", None, "disabled")
        return None

    try:
        import boto3
        region = os.getenv("BEDROCK_REGION")
        model_id = os.getenv("CLAUDE_MODEL_ID", "anthropic.claude-3-5-haiku-20241022-v1:0")
        client = boto3.client("bedrock-runtime", region_name=region)

        user_text = (
            "You are IssueCoin, a warm, non-judgmental finance buddy. "
            "From this JSON purchase context, respond with ONE short, funny motivational line "
            "in the same language as 'lang'. Keep it under 140 chars.\n\n"
            f"{json.dumps(context, ensure_ascii=False)}"
        )

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 120,
            "temperature": 0.6,
            "top_p": 0.9,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": user_text}]}
            ]
        })

        resp = client.invoke_model(
            modelId=model_id,
            body=body,
            accept="application/json",
            contentType="application/json"
        )

        payload = json.loads(resp.get("body").read().decode("utf-8"))
        content = payload.get("content", [])
        out = ""
        if content and isinstance(content, list) and "text" in content[0]:
            out = content[0]["text"].strip()
        out = out.replace("\n", " ").strip()
        return out if out else None

    except Exception as e:
        return None
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

# ---------------------------
# Handle submit
# ---------------------------
if submit:
    code = COUNTRY_TO_CODE[country]
    per_unit, rate_date = get_rate_for(code, d)
    if per_unit is None:
        st.error(TEXTS[LANG]["rate_err"])
    else:
        converted = round(amount * per_unit, 2)
        new_row = pd.DataFrame([{
            "Date": d.isoformat(), "Country": country, "Currency": code, "Amount": amount,
            "Category": category, "Shop": shop, "Note": note,
            "Converted_CZK": converted, "Rate_value": round(per_unit, 4), "Rate_date": rate_date
        }])
        st.session_state["expenses"] = pd.concat([st.session_state["expenses"], new_row], ignore_index=True)
        st.success(f"{TEXTS[LANG]['saved_ok']} {converted} CZK — "
                   f"{TEXTS[LANG]['rate_info']}: {round(per_unit,4)} CZK/1 {code} "
                   f"({TEXTS[LANG]['rate_from']} {rate_date})")

        # Friendly threshold nudges (legacy)
        df_now = st.session_state["expenses"]
        sums = df_now.groupby("Category")["Converted_CZK"].sum() if not df_now.empty else pd.Series(dtype=float)
        if any(k in sums.index and sums[k] > 5000 for k in ["Potraviny 🛒 / Potraviny 🛒", "Groceries 🛒"]):
            st.info("🍎 " + ("Potraviny niečo stoja – pri väčšej rodine je to prirodzené. 😉"
                             if LANG=="sk" else "Groceries are pricey – with a bigger family, that’s normal. 😉"))
        if any(k in sums.index and sums[k] > 1500 for k in ["Zábava 🎉 / Zábava 🎉", "Entertainment 🎉"]):
            st.warning("🎉 " + ("Zábavy nikdy nie je dosť! Len pozor, aby ti ešte zostalo aj na chlebík. 😉"
                                if LANG=="sk" else "There’s never too much fun! Just keep a little left for bread. 😉"))
        if any(k in sums.index and sums[k] > 2000 for k in ["Drogérie 🧴 / Drogérie 🧴", "Drugstore 🧴"]):
            st.info("🧴 " + ("Drogéria je drahá, hlavne keď sú v tom deti. 😉"
                              if LANG=="sk" else "Drugstore items can be expensive, especially with kids. 😉"))
        if ("Elektronika" in category) or ("Electronics" in category):
            st.info("💻 " + ("Nový kúsok? Nech dlho slúži a uľahčí deň. 🚀"
                             if LANG=="sk" else "New gadget? May it last and make life easier. 🚀"))

        # Holiday context
        cc = resolve_country_for_calendarific(country)
        api_key = _calendarific_key()
        hols = calendarific_holidays(api_key, cc, d.year, d.month, d.day) if api_key else []

        # IssueCoin seasonal + holiday + general fun (always)
        issuecoin_block_show(d, hols, LANG)

        # Claude Haiku 4.5 hint (optional; if disabled, zobrazíme info)
        ctx = {"lang": LANG, "date": d.isoformat(), "country": country, "currency": code,
               "amount": amount, "category": category, "shop": shop, "note": note,
               "converted_czk": converted}
        hint = claude_haiku_45_init(ctx)
        
        if hint:
            st.success(f"🧠 Claude Haiku 4.5 says: {hint}")
        else:
            st.caption(TEXTS[LANG]["claude_haiku_off"])

# ---------------------------
# Table + summary
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
        ).properties(width=600, height=300)
    )
    st.altair_chart(chart, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(TEXTS[LANG]["export"], csv, f"expenses_{dt_date.today().isoformat()}.csv", "text/csv")

# ---------------------------
# Debug panel (optional)
# ---------------------------
def _badge(section: str):
    it = st.session_state.DEBUG[section]
    ok, ts, msg = it["ok"], (it["ts"] or "--:--:--"), (it["msg"] or "")
    if ok is None: cls, label = "badge-off", "OFF"
    elif ok:      cls, label = "badge-ok", "OK"
    else:         cls, label = "badge-err", "ERR"
    st.markdown(f'<span class="{cls}">{label}</span> <small>{ts}</small> — {msg}', unsafe_allow_html=True)

if show_debug:
    st.markdown("### 🧪 Debug panel")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("**CNB TXT**"); _badge("cnb")
    with c2: st.markdown("**Calendarific**"); _badge("calendarific")
    with c3:
        st.markdown("**Claude Haiku 4.5**"); _badge("Claude Haiku")
        last = st.session_state.DEBUG["claude_haiku"].get("last_hint")
        if last: st.code(last)
