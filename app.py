import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- Google Sheets setup ---
# Load JSON credentials from Streamlit Secrets
creds_json = st.secrets["gcp_service_account"]["credentials"]
creds_dict = json.loads(creds_json)

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open the Google Sheet (make sure the name matches your sheet)
sheet = client.open("DASS21_Results_Malay").sheet1

# --- Soalan DASS21 dalam Bahasa Melayu ---
questions_texts = [
    "Saya rasa susah untuk bertenang",
    "Saya sedar mulut saya rasa kering",
    "Saya seolah-olah tidak dapat mengalami perasaan positif sama sekali",
    "Saya mengalami kesukaran bernafas (contohnya, bernafas terlalu cepat, tercungap-cungap walaupun tidak melakukan aktiviti fizikal)",
    "Saya rasa tidak bersemangat untuk memulakan sesuatu keadaan",
    "Saya cenderung bertindak secara berlebihan kepada sesuatu keadaan",
    "Saya pernah menggeletar (contohnya tangan)",
    "Saya rasa saya terlalu gelisah",
    "Saya risau akan berlaku keadaan di mana saya panik dan berkelakuan bodoh",
    "Saya rasa tidak ada yang saya harapkan (putus harapan)",
    "Saya dapati saya mudah resah",
    "Saya merasa sukar untuk relaks",
    "Saya rasa muram dan sedih",
    "Saya tidak boleh terima apa jua yang menghalangi saya daripada meneruskan apa yang saya sedang lakukan",
    "Saya rasa hampir panik",
    "Saya tidak bersemangat langsung",
    "Saya rasa diri saya tidak berharga",
    "Saya mudah tersinggung",
    "Walaupun saya tidak melakukan aktiviti fizikal, saya sedar akan debaran jantung saya (contoh: degupan jantung lebih cepat)",
    "Saya rasa takut tanpa sebab",
    "Saya rasa hidup ini tidak beerti lagi"
]

# Kategori soalan
categories = {
    "Stres": [1, 6, 8, 11, 12, 14, 18],
    "Anzieti": [2, 4, 7, 9, 15, 19, 20],
    "Kemurungan": [3, 5, 10, 13, 16, 17, 21]
}

# Skala jawapan
options = {
    0: "Tidak pernah sama sekali",
    1: "Jarang",
    2: "Kerap",
    3: "Sangat kerap"
}

# --- UI ---
st.title("Saringan Minda Sihat - DASS21 (Bahasa Melayu)")

# Tambah ruangan untuk Nama / ID
student_name = st.text_input("Nama / ID Pelajar (Optional)")

responses = {}
for i, q in enumerate(questions_texts, start=1):
    responses[i] = st.radio(f"{i}. {q}", list(options.keys()), format_func=lambda x: options[x], index=0)

if st.button("Hantar"):
    # Kira skor
    scores = {}
    for kategori, qnums in categories.items():
        scores[kategori] = sum(responses[q] for q in qnums)

    # Interpretasi tahap (rujuk dokumen DASS21 versi BM)
    severity = {
        "Kemurungan": [(0,5,"Normal"), (6,7,"Ringan"), (8,10,"Sederhana"), (11,14,"Teruk"), (15,100,"Sangat Teruk")],
        "Anzieti": [(0,4,"Normal"), (5,6,"Ringan"), (7,8,"Sederhana"), (9,10,"Teruk"), (11,100,"Sangat Teruk")],
        "Stres": [(0,7,"Normal"), (8,9,"Ringan"), (10,13,"Sederhana"), (14,17,"Teruk"), (18,100,"Sangat Teruk")]
    }

    results = {}
    for kategori, value in scores.items():
        tahap = next(label for low, high, label in severity[kategori] if low <= value <= high)
        results[f"Tahap_{kategori}"] = tahap

    # Papar keputusan kepada pelajar
    st.subheader("Keputusan Anda")
    for kategori in categories.keys():
        st.write(f"**{kategori}: {scores[kategori]} → {results[f'Tahap_{kategori}']}**")

    # Simpan ke Google Sheets
    row = [
        str(datetime.datetime.now()),
        student_name
    ] + list(responses.values()) + [
        scores["Stres"], scores["Anzieti"], scores["Kemurungan"],
        results["Tahap_Stres"], results["Tahap_Anzieti"], results["Tahap_Kemurungan"]
    ]
    sheet.append_row(row)

    st.success("✅ Jawapan anda telah direkodkan ke Google Sheets.")
