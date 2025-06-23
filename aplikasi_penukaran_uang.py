import streamlit as st
import pandas as pd
from datetime import datetime

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Rekap Keuangan & Profit", layout="wide")
st.title("💸 Rekapitulasi Keuangan & Profit Kegiatan")

# --- Inisialisasi session_state untuk menyimpan data ---
# Menambah kolom 'nominal_qris' dan menghapus 'nama'
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=["waktu", "sesi", "jenis", "total_transaksi", "via_qris", "nominal_qris"])

# --- Sidebar untuk Modal ---
st.sidebar.header("🪙 Modal Awal")
total_modal = st.sidebar.number_input("Total Modal Awal (Rp)", value=26000000, step=100000)
st.sidebar.markdown(f"**Total Modal:** Rp {total_modal:,.0f}")

# --- Pilihan Sesi Kegiatan ---
# Membuat daftar pilihan untuk sesi kegiatan
sesi_kegiatan_options = [
    "Uang Modal",
    "Tortor Khusus Remaja",
    "Tortor Khusus Naposo",
    "Lelang Makanan",
    "Sumbangan Sukarela",
    "Lainnya"
]

# --- Form Input Transaksi ---
st.subheader("📝 Input Transaksi Baru")
with st.form("form_input", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        sesi = st.selectbox("Sesi Kegiatan", sesi_kegiatan_options)
        jenis_transaksi = st.selectbox("Jenis Transaksi", ["Penukaran", "Donasi"])
        
    with col2:
        # Mengubah label menjadi lebih jelas
        total_transaksi = st.number_input("Uang Masuk / Uang Keluar (-) (Rp)", step=1000)
        via_qris = st.checkbox("Via QRIS?")
        
        # Input nominal QRIS akan muncul jika checkbox dicentang
        nominal_qris = 0
        if via_qris:
            nominal_qris = st.number_input("Nominal QRIS (Rp)", min_value=0, step=1000, help="Isi jumlah yang ditransaksikan via QRIS dari Total Transaksi.")

    submitted = st.form_submit_button("✅ Tambah Transaksi")

# --- Proses Penyimpanan Data ---
if submitted:
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_data = {
        "waktu": waktu,
        "sesi": sesi,
        "jenis": jenis_transaksi,
        "total_transaksi": total_transaksi,
        "via_qris": "Ya" if via_qris else "Tidak",
        "nominal_qris": nominal_qris
    }
    
    # Menggunakan pd.concat untuk menambahkan data baru
    st.session_state["data"] = pd.concat([st.session_state["data"], pd.DataFrame([new_data])], ignore_index=True)
    st.success("Transaksi berhasil ditambahkan!")

# Ambil data dari session_state
data = st.session_state["data"]

# --- Tampilan Data Transaksi ---
st.subheader("📊 Seluruh Data Transaksi")
# Memastikan urutan kolom sesuai dan menampilkan DataFrame
if not data.empty:
    display_cols = ["waktu", "sesi", "jenis", "total_transaksi", "via_qris", "nominal_qris"]
    st.dataframe(data[display_cols], use_container_width=True)
else:
    st.info("Belum ada data transaksi.")


# --- Rekapitulasi Keseluruhan ---
st.subheader("📈 Rekapitulasi Keseluruhan")
if not data.empty:
    penukaran = data[data["jenis"] == "Penukaran"]
    donasi = data[data["jenis"] == "Donasi"]

    # Menghitung total berdasarkan kolom 'total_transaksi' dan 'nominal_qris'
    total_uang_masuk_penukaran = penukaran["total_transaksi"].sum()
    total_qris_penukaran = penukaran["nominal_qris"].sum()

    total_uang_donasi = donasi["total_transaksi"].sum()
    total_qris_donasi = donasi["nominal_qris"].sum()
    
    total_keseluruhan = data["total_transaksi"].sum()
    total_qris_keseluruhan = data["nominal_qris"].sum()
    total_tunai_keseluruhan = total_keseluruhan - total_qris_keseluruhan

    col_rekap1, col_rekap2 = st.columns(2)
    with col_rekap1:
        st.markdown(f"### 💰 Ringkasan Transaksi")
        st.metric("Total Penukaran", f"Rp {total_uang_masuk_penukaran:,.0f}")
        st.metric("Total Penukaran via QRIS", f"Rp {total_qris_penukaran:,.0f}")
    
    with col_rekap2:
        st.markdown(f"### 🎁 Donasi & Profit")
        st.metric("Total Donasi (Profit)", f"Rp {total_uang_donasi:,.0f}")
        st.metric("Total Donasi via QRIS", f"Rp {total_qris_donasi:,.0f}")

    st.markdown("---")
    st.markdown(f"### 💵 Ringkasan Keuangan Akhir")
    col_akhir1, col_akhir2, col_akhir3 = st.columns(3)
    col_akhir1.metric("Total Pemasukan (Penukaran + Donasi)", f"Rp {total_keseluruhan:,.0f}")
    col_akhir2.metric("Total Uang Tunai di Tangan", f"Rp {total_tunai_keseluruhan:,.0f}")
    col_akhir3.metric("Total Pemasukan via QRIS", f"Rp {total_qris_keseluruhan:,.0f}")

else:
    st.info("Belum ada data untuk direkapitulasi.")

# --- Rekapitulasi per Sesi Kegiatan ---
st.subheader("🔎 Rekapitulasi per Sesi")
if not data.empty:
    sesi_unik = data["sesi"].unique()
    for sesi_item in sesi_unik:
        with st.expander(f"Rincian Sesi: **{sesi_item}**"):
            data_sesi = data[data["sesi"] == sesi_item]
            
            total_sesi = data_sesi["total_transaksi"].sum()
            qris_sesi = data_sesi["nominal_qris"].sum()
            tunai_sesi = total_sesi - qris_sesi
            
            # Memisahkan donasi dan penukaran untuk sesi ini
            donasi_sesi = data_sesi[data_sesi["jenis"] == "Donasi"]["total_transaksi"].sum()
            penukaran_sesi = data_sesi[data_sesi["jenis"] == "Penukaran"]["total_transaksi"].sum()

            st.markdown(f"- **Total Pemasukan Sesi Ini:** Rp {total_sesi:,.0f}")
            st.markdown(f"- **Total Tunai:** Rp {tunai_sesi:,.0f}")
            st.markdown(f"- **Total QRIS:** Rp {qris_sesi:,.0f}")
            st.markdown(f"- *Rincian: Total Donasi Rp {donasi_sesi:,.0f} & Total Penukaran Rp {penukaran_sesi:,.0f}*")
else:
    st.info("Tidak ada sesi untuk ditampilkan.")


# --- Opsi Export dan Hapus Data ---
st.subheader("⚙️ Opsi Data")
col_export1, col_export2 = st.columns(2)
with col_export1:
    # Mengubah data menjadi CSV untuk di-download
    csv_data = data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Data sebagai CSV",
        data=csv_data,
        file_name=f"rekap_keuangan_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

with col_export2:
    if st.button("🗑️ Hapus Semua Data"):
        # Kolom disesuaikan dengan struktur baru
        st.session_state["data"] = pd.DataFrame(columns=["waktu", "sesi", "jenis", "total_transaksi", "via_qris", "nominal_qris"])
        st.experimental_rerun()
