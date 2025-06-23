import streamlit as st
import pandas as pd
from datetime import datetime

# --- Setup halaman ---
st.set_page_config(page_title="Rekap Tukaran Uang & Profit", layout="wide")
st.title("💸 Rekapitulasi Tukaran Uang & Profit Jemaat")

# Inisialisasi data jika belum ada
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=["waktu", "sesi", "nama", "jenis", "uang_masuk", "via_qris"])

# Sidebar modal
st.sidebar.header("🪙 Modal Awal")
total_modal = st.sidebar.number_input("Total Modal Awal (Rp)", value=26000000, step=100000)
st.sidebar.markdown(f"**Total Modal:** Rp {total_modal:,.0f}")

# Form input
st.subheader("📝 Input Transaksi")
with st.form("form_input"):
    col1, col2 = st.columns(2)
    with col1:
        nama = st.text_input("Nama Jemaat")
        sesi = st.text_input("Sesi Kegiatan", placeholder="Misal: Parheheon")
        jenis_transaksi = st.selectbox("Jenis Transaksi", ["Penukaran", "Donasi"])
    with col2:
        via_qris = st.checkbox("Via QRIS?")
        uang_masuk = st.number_input("Uang Masuk (Rp)", step=1000)

    submitted = st.form_submit_button("+ Tambah Transaksi")

# Simpan data ke session_state
if submitted:
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = {
        "waktu": waktu,
        "sesi": sesi,
        "nama": nama,
        "jenis": jenis_transaksi,
        "uang_masuk": uang_masuk,
        "via_qris": "Ya" if via_qris else "Tidak"
    }
    st.session_state["data"] = pd.concat([st.session_state["data"], pd.DataFrame([new_data])], ignore_index=True)
    st.success("Transaksi berhasil ditambahkan!")

# Ambil data
data = st.session_state["data"]

# Tampilkan data
st.subheader("📊 Data Transaksi")
st.dataframe(data, use_container_width=True)

# Rekapitulasi
st.subheader("📈 Rekapitulasi")
if not data.empty:
    penukaran = data[data["jenis"] == "Penukaran"]
    donasi = data[data["jenis"] == "Donasi"]

    total_uang_masuk_penukaran = penukaran["uang_masuk"].sum()
    total_qris_penukaran = penukaran[penukaran["via_qris"] == "Ya"]["uang_masuk"].sum()

    total_uang_donasi = donasi["uang_masuk"].sum()
    total_qris_donasi = donasi[donasi["via_qris"] == "Ya"]["uang_masuk"].sum()

    st.markdown(f"### 💰 Ringkasan Transaksi")
    st.markdown(f"- Total Penukaran (tunai + QRIS): **Rp {total_uang_masuk_penukaran:,.0f}**")
    st.markdown(f"- Total QRIS Penukaran: **Rp {total_qris_penukaran:,.0f}**")

    st.markdown("---")
    st.markdown(f"### 🎁 Donasi & Profit")
    st.markdown(f"- Total Donasi Tunai: **Rp {total_uang_donasi - total_qris_donasi:,.0f}**")
    st.markdown(f"- Total QRIS Donasi: **Rp {total_qris_donasi:,.0f}**")
    st.markdown(f"- **Total Profit (Semua Donasi): Rp {total_uang_donasi:,.0f}**")
else:
    st.info("Belum ada data transaksi.")

# Export / Hapus
st.subheader("⬇️ Export Data")
col_export1, col_export2 = st.columns(2)
with col_export1:
    csv_data = data.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv_data, "data_transaksi.csv", "text/csv")

with col_export2:
    if st.button("🗑️ Hapus Semua Data"):
        st.session_state["data"] = pd.DataFrame(columns=data.columns)
        st.warning("Semua data telah dihapus.")
