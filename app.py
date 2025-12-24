import streamlit as st
import sqlite3
from PIL import Image
import io
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# -----------------------------
# GOOGLE DRIVE AUTH
# -----------------------------
@st.cache_resource
def connect_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Opens browser for login
    return GoogleDrive(gauth)

drive = connect_drive()

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect("invoices.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    invoice_no TEXT PRIMARY KEY,
    file_id TEXT,
    type TEXT
)
""")
conn.commit()

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("🌿 Fern n Petal – Invoice Manager")

menu = ["Upload Invoice", "Search Invoice"]
choice = st.sidebar.selectbox("Menu", menu)

# -----------------------------
# UPLOAD PAGE
# -----------------------------
if choice == "Upload Invoice":
    st.header("Upload Invoice to Google Drive")

    invoice_no = st.text_input("Enter Invoice Number")

    # Checkbox field
    doc_type = st.radio("Select Document Type", ["Invoice", "Delivery Note"])

    uploaded_file = st.file_uploader("Upload Invoice Image", type=["jpg", "jpeg", "png"])

    if st.button("Upload"):
        if invoice_no and uploaded_file:
            # Upload to Google Drive
            file_drive = drive.CreateFile({'title': f"{invoice_no}.jpg"})
            file_drive.SetContentBytes(uploaded_file.read())
            file_drive.Upload()

            file_id = file_drive['id']

            # Save metadata in DB
            cursor.execute("INSERT OR REPLACE INTO invoices VALUES (?, ?, ?)",
                           (invoice_no, file_id, doc_type))
            conn.commit()

            st.success(f"Uploaded successfully to Google Drive! File ID: {file_id}")
        else:
            st.error("Please enter invoice number and upload a file.")

# -----------------------------
# SEARCH PAGE
# -----------------------------
elif choice == "Search Invoice":
    st.header("Search Invoice")

    search_no = st.text_input("Enter Invoice Number to Search")

    if st.button("Search"):
        cursor.execute("SELECT file_id, type FROM invoices WHERE invoice_no = ?", (search_no,))
        result = cursor.fetchone()

        if result:
            file_id, doc_type = result

            st.info(f"Document Type: {doc_type}")

            # Download from Google Drive
            file_drive = drive.CreateFile({'id': file_id})
            file_drive.GetContentFile("temp.jpg")

            img = Image.open("temp.jpg")
            st.image(img, caption=f"Invoice {search_no}", use_column_width=True)
        else:
            st.error("Invoice not found.")
