import streamlit as st
import pandas as pd
from datetime import datetime
import mysql.connector

# --- Konfigurasi koneksi MySQL ---
def koneksi_db():
    return mysql.connector.connect(
        host="localhost",       # Ganti jika pakai hosting
        user="root",            # Ganti sesuai user MySQL kamu
        password="", # Ganti sesuai password MySQL kamu
        database="keuangan_gereja"  # Pastikan database sudah dibuat
    )

# --- Inisialisasi dan Fungsi ---
def simpan_transaksi(waktu, sesi, nama, jenis, uang_masuk, via_qris):
    db = koneksi_db()
    cursor = db.cursor()
    sql = """
        INSERT INTO transaksi (waktu, sesi, nama, jenis, uang_masuk, via_qris)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    val = (waktu, sesi, nama, jenis, uang_masuk, via_qris)
    cursor.execute(sql, val)
    db.commit()
    db.close()


def ambil_semua_data():
    db = koneksi_db()
    df = pd.read_sql("SELECT * FROM transaksi ORDER BY waktu DESC", con=db)
    db.close()
    return df


def hapus_semua_data():
    db = koneksi_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM transaksi")
    db.commit()
    db.close()

# --- Streamlit UI ---
st.set_page_config(page_title="Rekap Tukaran Uang & Profit", layout="wide")
st.title("💸 Rekapitulasi Tukaran Uang & Profit Jemaat")

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

if submitted:
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    simpan_transaksi(waktu, sesi, nama, jenis_transaksi, uang_masuk, "Ya" if via_qris else "Tidak")
    st.success("Transaksi berhasil ditambahkan!")

# Tampilkan data
data = ambil_semua_data()
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
        hapus_semua_data()
        st.warning("Semua data telah dihapus. Silakan refresh halaman.")
