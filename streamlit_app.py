import streamlit as st
import re
import pandas as pd
import io
import fungsi 

st.sidebar.header("About")
st.sidebar.text("""
    READ CAREFULLY:\n
1. Pastikan nama kontak tim SO diawali nama panggilan. Cth : Juan ACCT ✅ Pak Juan Acct ❌\n
2. Untuk saat ini gunakan fitur copas manual saja.\n
3. Copy seluruh data, pastikan copy setiap chatnya dari nama hingga jam dari tiap chat ikut tercopy\n
4. Sangat disarankan menggunakan template berikut *khusus unrecord*:\n

LOC :\nBIN :\nPN :\nSN :\nQTY :\nREMARK :\n
""")

# Streamlit App
st.title("UNRECORD Extractor")
st.text("Sangat disarankan menggunakan template berikut *khusus unrecord*:")
st.code("LOC :\nBIN :\nPN :\nSN :\nQTY :\nREMARK :\n")

input_option = st.selectbox("Pilih Input:", ["Upload File .txt", "Copy-Paste Manual"])

chat_text = ""

if input_option == "Upload File .txt":
    uploaded_file = st.file_uploader("Upload File Chat (.txt)", type=["txt"])
    if uploaded_file is not None:
        chat_text = uploaded_file.read().decode("utf-8")
elif input_option == "Copy-Paste Manual":
    chat_text = st.text_area("Masukkan Teks Chat di sini", height=300)

if st.button("Process"):
    if chat_text.strip() == "":
        st.warning("Masukkan data chat terlebih dahulu.")
    else:
        if input_option == "Upload File .txt":
            df_result = fungsi.process_chat_text_file(chat_text)
        else:
            df_result = fungsi.process_chat_text_manual(chat_text)

        if df_result.empty:
            st.warning("Hasil kosong. Cek format chat dan kata kunci.")
        else:
            st.success(f"Berhasil memproses {len(df_result)} baris data.")
            st.dataframe(df_result)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_result.to_excel(writer, index=False, sheet_name='Sheet1')
            st.download_button(
                label="Download Excel",
                data=buffer.getvalue(),
                file_name="hasil_unrecord.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
