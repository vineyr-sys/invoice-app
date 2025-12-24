import streamlit as st
import sqlite3
from PIL import Image
import os

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect("invoices.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    invoice_no TEXT PRIMARY KEY,
    filename TEXT,
    doc_type TEXT
)
""")
conn.commit()

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Fern n Petal Invoice App", layout="centered")
st.title("🌿 Fern n Petal – Invoice Manager")

menu = ["Upload Invoice", "Search Invoice"]
choice = st.sidebar.selectbox("Menu", menu)

# -----------------------------
# UPLOAD PAGE
# -----------------------------
if choice == "Upload Invoice":
    st.header("Upload Invoice")

    invoice_no = st.text_input("Enter Invoice Number")

    # Checkbox field
    doc_type = st.radio("Select Document Type", ["Invoice", "Delivery Note"])

    uploaded_file = st.file_uploader("Upload Invoice Image", type=["jpg", "jpeg", "png"])

    if st.button("Upload"):
        if invoice_no and uploaded_file:
            # Save file locally
            uploads_dir = "uploads"
            os.makedirs(uploads_dir, exist_ok=True)

            file_path = os.path.join(uploads_dir, f"{invoice_no}.jpg")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            # Save metadata in DB
            cursor.execute("INSERT OR REPLACE INTO invoices VALUES (?, ?, ?)",
                           (invoice_no, file_path, doc_type))
            conn.commit()

            st.success(f"Uploaded successfully! Saved as {file_path}")
        else:
            st.error("Please enter invoice number and upload a file.")

# -----------------------------
# SEARCH PAGE
# -----------------------------
elif choice == "Search Invoice":
    st.header("Search Invoice")

    search_no = st.text_input("Enter Invoice Number to Search")

    if st.button("Search"):
        cursor.execute("SELECT filename, doc_type FROM invoices WHERE invoice_no = ?", (search_no,))
        result = cursor.fetchone()

        if result:
            filename, doc_type = result
            st.info(f"Document Type: {doc_type}")

            if os.path.exists(filename):
                img = Image.open(filename)
                st.image(img, caption=f"Invoice {search_no}", use_column_width=True)
            else:
                st.error("Image file not found.")
        else:
            st.error("Invoice not found.")
