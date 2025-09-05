import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Hide Streamlit default UI elements (menu, footer, header, GitHub icon, Manage app) ---
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}                  /* Hide hamburger menu */
    footer {visibility: hidden;}                     /* Hide footer */
    header {visibility: hidden;}                     /* Hide Streamlit header */
    a[data-testid="stAppGithubIcon"] {display: none !important;}  /* Hide GitHub icon (old selector) */
    div[data-testid="stToolbar"] {display: none !important;}      /* Hide GitHub icon (new toolbar) */
    div[data-testid="stDecoration"] {display: none !important;}   /* Hide Streamlit branding */
    div[data-testid="stConnectionStatus"] {display: none !important;}  /* Hide Manage app button */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Google Sheets setup ---
creds_dict = dict(st.secrets["gcp_service_account"])
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("DASS21_Results_Malay").sheet1

# --- General Information ---
st.title("Saringan Minda Sihat UniKL")

student_name = st.text_input("Nama")
student_id = st.text_input("Student ID")

# Dropdown list for Kampus
campus_list = [
    "Pilih Kampus", "MSI", "RCMP", "MIMET", "MIIT", "UBIS",
    "MIDI", "MESTECH", "MFI", "BMI", "MICET", "MITEC", "MIAT"
]
campus_name = st.selectbox("Kampus", campus_list)

phone_number = st.text_input("No. Telefon")

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

# Kategori soalan (mengikut manual DASS21)
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

# --- Display Questions ---
responses = {}
for i, q in enumerate(questions_texts, start=1):
    responses[i] = st.radio(
        f"{i}. {q}",
        list(options.keys()),
        format_func=lambda x: options[x],
        index=None
    )

# --- Submit Button ---
if st.button("Hantar"):
    # Validation: Student ID and Kampus must be filled
    if len(student_id.strip()) == 0:
        st.error("⚠️ Sila isi 'Student ID' sebelum menghantar borang.")
    elif campus_name == "Pilih Kampus":
        st.error("⚠️ Sila pilih 'Kampus' sebelum menghantar borang.")
    elif any(answer is None for answer in responses.values()):
        st.error("⚠️ Sila jawab semua soalan sebelum menghantar borang.")
    else:
        # Kira skor
        scores = {}
        for kategori, qnums in categories.items():
            scores[kategori] = sum(responses[q] for q in qnums)

        # Interpretasi tahap
        severity = {
            "Kemurungan": [(0,5,"Normal"), (6,7,"Ringan"), (8,10,"Sederhana"), (11,14,"Teruk"), (15,100,"Sangat Teruk")],
            "Anzieti": [(0,4,"Normal"), (5,6,"Ringan"), (7,8,"Sederhana"), (9,10,"Teruk"), (11,100,"Sangat Teruk")],
            "Stres": [(0,7,"Normal"), (8,9,"Ringan"), (10,13,"Sederhana"), (14,17,"Teruk"), (18,100,"Sangat Teruk")]
        }

        results = {}
        for kategori, value in scores.items():
            tahap = next(label for low, high, label in severity[kategori] if low <= value <= high)
            results[f"Tahap_{kategori}"] = tahap

        # Paparkan keputusan
        st.subheader("Keputusan Anda")
        for kategori in categories.keys():
            st.write(f"**{kategori}: {scores[kategori]} → {results[f'Tahap_{kategori}']}**")

        # Simpan ke Google Sheets
        row = [
            str(datetime.datetime.now()),
            student_name,
            student_id,
            campus_name,
            phone_number
        ] + list(responses.values()) + [
            scores["Stres"], scores["Anzieti"], scores["Kemurungan"],
            results["Tahap_Stres"], results["Tahap_Anzieti"], results["Tahap_Kemurungan"]
        ]
        sheet.append_row(row)

        st.success("✅ Jawapan anda telah direkodkan oleh Kaunselor UniKL")
