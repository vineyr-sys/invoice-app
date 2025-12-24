import streamlit as st
import sqlite3
import os
from PIL import Image

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_to_db(invoice_number, file_path):
    conn = sqlite3.connect("invoices.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_number TEXT, file_path TEXT)")
    c.execute("INSERT INTO invoices (invoice_number, file_path) VALUES (?, ?)", (invoice_number, file_path))
    conn.commit()
    conn.close()

def search_invoice(invoice_number):
    conn = sqlite3.connect("invoices.db")
    c = conn.cursor()
    c.execute("SELECT file_path FROM invoices WHERE invoice_number = ?", (invoice_number,))
    result = c.fetchone()
    conn.close()
    return result

st.title("🧾 Invoice Upload & Search")

menu = st.sidebar.radio("Choose Action", ["Upload Invoice", "Search Invoice"])

if menu == "Upload Invoice":
    st.header("Upload New Invoice")
    invoice_number = st.text_input("Enter Invoice Number")
    uploaded_file = st.file_uploader("Upload Invoice Image", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file and invoice_number:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        save_to_db(invoice_number, file_path)
        st.success("Invoice saved successfully!")

elif menu == "Search Invoice":
    st.header("Search Invoice by Number")
    search_number = st.text_input("Enter Invoice Number")

    if search_number:
        result = search_invoice(search_number)
        if result:
            st.success("Invoice found!")
            if result[0].endswith(".pdf"):
                st.write("PDF file found:", result[0])
            else:
                st.image(result[0])
        else:
            st.error("Invoice not found.")
