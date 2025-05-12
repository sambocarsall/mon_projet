import streamlit as st
import face_recognition
import numpy as np
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import io

# Configuration Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Présences").sheet1

# Chargement des visages connus
known_face_encodings = []
known_face_names = []

import os
for filename in os.listdir("faces"):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image = face_recognition.load_image_file(f"faces/{filename}")
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_face_encodings.append(encoding[0])
            known_face_names.append(filename.split(".")[0].capitalize())

# Interface Streamlit
st.title("🎯 Pointage par Reconnaissance Faciale")
st.write("Charge une photo pour vérifier et enregistrer l’arrivée.")

uploaded_file = st.file_uploader("📸 Charge une image (JPG ou PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Image chargée", use_column_width=True)

    # Conversion image en array
    img_array = np.array(img)

    # Encodage visage
    face_locations = face_recognition.face_locations(img_array)
    face_encodings = face_recognition.face_encodings(img_array, face_locations)

    if face_encodings:
        found = False
        for encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, encoding)
            if True in matches:
                index = matches.index(True)
                name = known_face_names[index]
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([name, now])
                st.success(f"✅ {name} enregistré à {now}")
                found = True
                break
        if not found:
            st.warning("😕 Visage inconnu. Aucune correspondance.")
    else:
        st.error("❌ Aucun visage détecté.")
