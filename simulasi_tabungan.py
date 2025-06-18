import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import dateutil.relativedelta # Diperlukan untuk penambahan bulan yang akurat
# Pastikan Anda sudah menginstal: pip install python-dateutil

# --- Fungsi Bantuan untuk Format Rupiah ---
def format_rupiah(value):
    """
    Memformat angka float menjadi string mata uang Rupiah (contoh: Rp 1.000.000,50).
    """
    value = float(value)
    s = "{:,.2f}".format(value) # Hasilnya seperti "1,234,567.89"
    s = s.replace('.', '#')      # Ganti titik desimal sementara dengan '#'
    s = s.replace(',', '.')      # Ganti koma ribuan dengan '.'
    s = s.replace('#', ',')      # Ganti '#' dengan koma desimal
    return "Rp " + s


# --- Pengaturan Halaman Streamlit (HARUS JADI YANG PERTAMA) ---
st.set_page_config(
    page_title="Simulasi Pertumbuhan Tabungan dengan Bunga Berkelanjutan",
    page_icon="💰",
    layout="centered"
)

# --- CSS Kustom untuk Ukuran Font dan Kerapian ---
st.markdown(
    """
    <style>
    /* Mengatur font dasar untuk sebagian besar teks */
    body, .stApp, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        font-family: "sans serif", Arial, sans-serif;
        font-size: 18px !important;
        line-height: 1.5;
    }

    /* Judul Utama */
    h1 {
        font-size: 50px !important;
        color: #FF69B4;
        text-align: center;
        margin-bottom: 0.5em;
        line-height: 1.2;
    }
    /* Subheader seperti "Ringkasan Input Anda", "Visualisasi", "Detail Tabel" */
    h2 {
        font-size: 32px !important;
        padding-top: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #FFC0CB;
        line-height: 1.3;
    }
    /* Untuk st.info dan st.success yang muncul sementara */
    [data-testid="stInfo"] p, [data-testid="stSuccess"] p {
        font-size: 18px !important;
        text-align: center;
    }
    /* Mengatur ukuran font untuk angka di metrik (Ringkasan Input) */
    [data-testid="stMetricValue"] {
        font-size: 40px !important;
        font-weight: bold !important;
        margin-bottom: -0.1em;
    }
    /* Mengatur ukuran font untuk label di bawah angka metrik */
    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        white-space: normal !important;
        text-align: center;
        min-height: 2em;
    }
    /* Menyesuaikan lebar kolom untuk Ringkasan Input agar tidak berantakan */
    [data-testid="stColumn"] {
        flex: 1 1 250px !important; /* FIXED: Min-width ditingkatkan dari 200px ke 250px */
        padding: 5px !important;
        margin: 0 !important;
        align-items: flex-start;
        min-height: 100px;
    }

    /* Penyesuaian spesifik untuk sidebar input dan tombol */
    div[data-testid="stSidebar"] *,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stCheckbox"] label,
    div[data-testid="stButton"] button,
    div[data-testid="stText"] p /* Added for general text in sidebar */
    {
        font-size: 18px !important;
    }
    .stButton > button {
        font-size: 20px !important;
        padding: 0.8em 1.8em !important;
        height: auto !important;
    }
    /* Mengatur ukuran font untuk data_editor (tabel jadwal bunga) */
    [data-testid="stDataEditorRow"] > div {
        font-size: 16px !important;
    }
    [data-testid="stDataEditorHeader"] > div {
        font-size: 14px !important;
    }

    /* Untuk teks paragraf umum seperti deskripsi aplikasi */
    p {
        font-size: 18px !important;
        line-height: 1.5;
    }
    .main [data-testid="stVerticalBlock"] > div:first-child {
        margin-bottom: -10px;
    }
    /* === Styling Sidebar === */
    div[data-testid="stSidebar"] {
        background-color: #FFF0F5; /* Background sesuai tema */
        background: linear-gradient(to bottom, #FFE5EE, #FFF0F5); /* Gradient lembut */
        border-right: 1px solid #FFD1DC; /* Border tipis */
        box-shadow: 2px 0 8px rgba(0,0,0,0.1); /* Shadow untuk kedalaman */
        padding-top: 2em;
        padding-left: 1.5em;
        padding-right: 1.5em;
    }

    /* Header di Sidebar */
    div[data-testid="stSidebar"] h1,
    div[data-testid="stSidebar"] h2,
    div[data-testid="stSidebar"] h3 {
        color: #FF69B4 !important; /* Warna pink untuk header */
        font-weight: bold;
        border-bottom: 2px solid #FFC0CB; /* Garis bawah pemisah */
        padding-bottom: 0.5em;
        margin-bottom: 1.5em; /* Jarak bawah */
    }
     
    /* Styling Radio Button di Sidebar (navigasi utama dan sub-mode) */
    div[data-testid="stRadio"] label {
        background-color: #F8F0F5; /* Background untuk setiap opsi */
        padding: 0.8em 1em;
        margin-bottom: 0.6em; /* Jarak antar opsi */
        border-radius: 10px;
        border: 1px solid #FFD1DC; /* Border lembut */
        transition: all 0.2s ease-in-out; /* Efek transisi */
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
        color: #2F4F4F; /* Warna teks default */
        font-weight: normal;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: #FFE5EE; /* Lighter pink on hover */
        border-color: #FF69B4; /* Border pink saat hover */
    }
    div[data-testid="stRadio"] input[type="radio"]:checked + div {
        background-color: transparent !important; /* FIXED: Hapus background highlight */
        border-color: #FF69B4 !important; /* Border pink saat terpilih tetap ada */
        color: #4B0082 !important; /* Teks ungu gelap saat terpilih */
        font-weight: bold;
        box-shadow: none !important; /* FIXED: Hapus shadow highlight */
    }

    /* Input Fields di Sidebar (NumberInput, DateInput, DataEditor) */
    div[data-testid="stSidebar"] div[data-testid="stNumberInput"] div[data-testid="stInputContainer"],
    div[data-testid="stSidebar"] div[data-testid="stDateInput"] div[data-testid="stInputContainer"],
    div[data-testid="stSidebar"] div[data-testid="stCheckbox"] label,
    div[data-testid="stSidebar"] div[data-testid="stDataFrame"] {
        background-color: #FFFFFF; /* Background putih untuk input */
        border: 1px solid #FFD1DC;
        border-radius: 8px;
        padding: 0.5em;
        margin-bottom: 1em;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); /* Inner shadow */
    }
    /* Info box di sidebar (misal untuk panduan jadwal bunga) */
    div[data-testid="stSidebar"] [data-testid="stInfo"] {
        background-color: #FFE5EE;
        border-left: 5px solid #FF69B4;
        border-radius: 5px;
        padding: 0.8em;
        margin-bottom: 1em;
    }

    /* Styling tombol */
    .stButton > button {
        font-size: 20px !important;
        padding: 0.8em 1.8em !important;
        height: auto !important;
        background-color: #FF69B4; /* Background pink tombol */
        color: white; /* Teks putih tombol */
        border-radius: 10px;
        border: none;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        transition: background-color 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #E04F90; /* Darker pink on hover */
        color: white;
    }

    /* Untuk teks paragraf umum seperti deskripsi aplikasi */
    p {
        font-size: 18px !important;
        line-height: 1.5;
    }
    /* Penyesuaian margin umum */
    .main [data-testid="stVerticalBlock"] > div:first-child {
        margin-bottom: -10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- 1. Logika Inti Perhitungan ---

# Fungsi UTAMA untuk menangani semua skenario perhitungan bulanan (tanpa dana tambahan)
# is_bunga_tahunan: True jika bunga_konstan_persen adalah bunga tahunan, False jika bunga bulanan
def hitung_pertumbuhan_bulanan(jumlah_awal, jadwal_bunga_persen, durasi_bulan_total, bunga_konstan_persen, is_bunga_konstan_tahunan, start_date):
    hasil_per_bulan = []
     
    # rates_by_start_month akan menyimpan rate desimal yang akan langsung digunakan dalam math.exp()
    # Jadi, jika input adalah tahunan, kita bagi 12 di sini. Jika bulanan, langsung pakai.
    rates_by_start_month = {}

    if jadwal_bunga_persen is not None: # Mode Bunga Berubah-ubah (Bunga Bulanan)
        for item in jadwal_bunga_persen:
            start_month_total = int(item['Bulan Mulai'])
            # Bunga yang diinput di jadwal adalah BULANAN, jadi langsung dibagi 100
            rate_desimal = float(item['Bunga Bulanan (%)']) / 100.0 
            rates_by_start_month[start_month_total] = rate_desimal
    else: # Mode Bunga Konstan
        rate_desimal_konstan = bunga_konstan_persen / 100.0
        if is_bunga_konstan_tahunan:
            # Jika bunga konstan adalah TAHUNAN, bagi 12 untuk dapatkan rate bulanan untuk continuous compounding
            rates_by_start_month[1] = rate_desimal_konstan / 12
        else:
            # Jika bunga konstan adalah BULANAN, langsung gunakan rate desimal bulanan
            rates_by_start_month[1] = rate_desimal_konstan

    current_saldo = jumlah_awal
     
    # Ambil bunga bulanan awal yang berlaku untuk Bulan 1.
    # Jika rates_by_start_month kosong (misal data_editor kosong), set ke 0.0
    current_effective_monthly_rate = rates_by_start_month.get(1, 0.0)

    # Inisialisasi tanggal perhitungan
    current_calculated_date = start_date
     
    # Tambahkan saldo awal di tanggal awal simulasi (Ini adalah entri untuk Bulan 0)
    hasil_per_bulan.append({
        'Tanggal': current_calculated_date.strftime("%d %B %Y"),
        'Jumlah Uang (Rp)': current_saldo
    })

    # Loop untuk setiap bulan simulasi, dari Bulan 1 hingga durasi_bulan_total
    for total_month_num in range(1, durasi_bulan_total + 1):
        date_for_this_entry = start_date + dateutil.relativedelta.relativedelta(months=total_month_num)
         
        # Perbarui bunga jika ada perubahan di awal bulan ini (sesuai total_month_num)
        if total_month_num in rates_by_start_month:
            current_effective_monthly_rate = rates_by_start_month[total_month_num]
        
        # Hitung faktor pertumbuhan bulanan untuk bunga majemuk kontinu
        # current_effective_monthly_rate sudah dalam format yang benar untuk math.exp()
        growth_factor_monthly = math.exp(current_effective_monthly_rate) if current_effective_monthly_rate != 0 else 1.0
         
        # Terapkan pertumbuhan untuk bulan ini
        current_saldo = current_saldo * growth_factor_monthly
         
        # Tambahkan hasil untuk bulan ini ke daftar
        hasil_per_bulan.append({
            'Tanggal': date_for_this_entry.strftime("%d %B %Y"),
            'Jumlah Uang (Rp)': current_saldo
        })
     
    return hasil_per_bulan

# Fungsi untuk menghitung durasi target
# bunga_estimasi_persen: Bunga dalam persen (Tahunan jika mode bunga konstan, Bulanan jika mode bunga berubah-ubah)
# is_bunga_target_tahunan: True jika bunga_estimasi_persen adalah bunga tahunan, False jika bulanan
def hitung_durasi_target(jumlah_awal, target_jumlah, bunga_estimasi_persen, is_bunga_target_tahunan, start_date):
    if bunga_estimasi_persen <= 0:
        return "Bunga harus lebih besar dari 0% untuk mencapai target (tanpa dana tambahan)."
     
    if jumlah_awal >= target_jumlah:
        return "Target sudah tercapai atau saldo awal sudah lebih besar!"

    try:
        rate_desimal = bunga_estimasi_persen / 100.0
        
        if is_bunga_target_tahunan:
            # Gunakan rate tahunan langsung untuk formula durasi tahunan
            durasi_tahun_float = math.log(target_jumlah / jumlah_awal) / rate_desimal
            durasi_bulan_float = durasi_tahun_float * 12
        else:
            # Jika bunga bulanan, gunakan langsung rate bulanan untuk formula durasi bulanan
            durasi_bulan_float = math.log(target_jumlah / jumlah_awal) / rate_desimal
         
        durasi_bulan_int = math.ceil(durasi_bulan_float)
         
        # Hitung tanggal target
        target_date = start_date + dateutil.relativedelta.relativedelta(months=durasi_bulan_int)

        return (durasi_bulan_int, target_date)

    except ValueError:
        return "Input tidak valid untuk perhitungan logaritma."


# --- 2. Tampilan UI Streamlit ---

st.title("💰Simulasi Pertumbuhan Tabungan")
st.markdown("Selamat datang di Sistem Simulasi Pertumbuhan Tabungan! Sistem ini dirancang untuk membantu Anda memahami bagaimana uang Anda dapat tumbuh seiring waktu dengan bunga majemuk kontinu.")
st.markdown("Sistem ini mensimulasikan pertumbuhan uang di tabungan dengan **bunga majemuk kontinu**.")
st.markdown("Pada sistem ini kita dapat melihat hasil pertumbuhan uang berdasarkan **saldo awal** dan **bunga** yang dapat bersifat konstan atau berubah seiring waktu.")


st.sidebar.header("Navigasi Sistem")

# Pilihan Mode Aplikasi Utama (Mengontrol Konten Area Utama)
mode_aplikasi_utama = st.sidebar.radio(
    "Pilih Mode Sistem:",
    ("Panduan Penggunaan", "Mulai Simulasi"),
    key="mode_aplikasi_utama_radio"
)
st.sidebar.write("---")


# --- KONTEN UTAMA BERDASARKAN MODE APLIKASI YANG DIPILIH ---

# Mode "Panduan Penggunaan" (Ini yang pertama)
if mode_aplikasi_utama == "Panduan Penggunaan":
    st.header("📚 Panduan Penggunaan Sistem")
    st.markdown("""

    ### 1. Mode Sistem

    Di sidebar (sisi kiri), Anda akan menemukan 2 pilihan mode utama:

    * **Panduan Penggunaan:** Halaman ini, tempat Anda menemukan informasi cara menggunakan sistem.
    * **Mulai Simulasi:** Ini adalah mode interaktif utama untuk menjalankan simulasi pertumbuhan atau mencari durasi target.

    ### 2. Pengaturan Simulasi (dalam Mode 'Mulai Simulasi')

    Saat Anda memilih mode **'Mulai Simulasi'**, sidebar akan menampilkan pengaturan berikut:

    * **Pilih Sub-Mode Simulasi:**
        * **Simulasi Pertumbuhan:** Untuk melihat grafik dan tabel pertumbuhan uang Anda selama durasi tertentu.
        * **Cari Durasi Target:** Untuk menghitung berapa lama waktu yang Anda butuhkan untuk mencapai target saldo yang Anda inginkan.
        
    * **Jumlah Uang Awal (Rp):** Masukkan jumlah uang awal yang ingin Anda simulasikan.
    
    * **Tanggal Mulai Simulasi:** Tentukan tanggal kapan simulasi ini dimulai. Hasil tabel dan grafik akan mengikuti tanggal ini.
    
    * **Aktifkan Bunga Berubah-ubah:**
        * Jika **tidak dicentang:** Anda akan menggunakan **satu nilai bunga secara konstan** sepanjang simulasi. Masukkan nilai bunga (dalam %) di kolom yang tersedia.
        * Jika **dicentang:** Anda dapat membuat **jadwal bunga yang berubah-ubah** per bulan. Masukkan 'Bulan Mulai (ke-)' (nomor bulan ke-berapa simulasi berjalan, dimulai dari 1) dan 'Bunga Bulanan (%)' yang berlaku dari bulan tersebut. Anda dapat menambah atau menghapus baris jadwal.

    ### 3. Menjalankan Simulasi / Mencari Durasi

    Setelah semua parameter diisi sesuai mode yang dipilih:

    * Jika di sub-mode **'Simulasi Pertumbuhan'**: Atur 'Durasi Simulasi (Bulan)', lalu klik tombol **"Jalankan Simulasi"**.
    * Jika di sub-mode **'Cari Durasi Target'**: Masukkan 'Target Jumlah Uang (Rp)', lalu klik tombol **"Cari Durasi"**.

    ### 4. Memahami Hasil

    * **Ringkasan Input Anda:** Menampilkan kembali parameter yang Anda masukkan.
    * **Visualisasi Grafik:** Menunjukkan bagaimana saldo Anda tumbuh secara visual. Sumbu X adalah 'Tanggal', dan sumbu Y adalah 'Jumlah Uang (Rp)'. Titik 'Nilai Akhir' akan menunjukkan saldo akhir Anda.
    * **Detail Pertumbuhan Uang per Bulan:** Menampilkan tabel rinci saldo Anda untuk setiap bulan simulasi.
    * **Estimasi Durasi Target:** Jika di mode 'Cari Durasi Target', sistem akan menampilkan jumlah bulan yang dibutuhkan dan tanggal perkiraan target akan tercapai.

    ---
    """)


# Mode "Mulai Simulasi" (Ini yang kedua)
elif mode_aplikasi_utama == "Mulai Simulasi":
    st.sidebar.subheader("Pengaturan Simulasi")

    # Pilihan Sub-Mode (Simulasi Pertumbuhan atau Cari Durasi Target)
    mode_simulasi_sub = st.sidebar.radio(
        "Pilih Sub-Mode Simulasi:",
        ("Simulasi Pertumbuhan", "Cari Durasi Target"),
        key="mode_simulasi_sub_radio"
    )
     
    # --- Input untuk kedua Sub-Mode Simulasi ---
    jumlah_awal = st.sidebar.number_input(
        "Jumlah Uang Awal (Rp)",
        min_value=0.0,
        value=1_000_000.0,
        step=100_000.0,
        format="%.2f"
    )

    # Input Tanggal Mulai Simulasi
    start_date = st.sidebar.date_input(
        "Tanggal Mulai Simulasi",
        value=datetime.today(), # Menggunakan tanggal hari ini sebagai default
        key="start_date_input"
    )


    # Checkbox untuk mengaktifkan bunga berubah-ubah
    ubah_bunga = st.sidebar.checkbox("Aktifkan Bunga Berubah-ubah")
    
    # Inisialisasi variabel untuk bunga (akan diisi di if/else di bawah)
    jadwal_bunga_persen = None
    bunga_konstan_persen_for_calc = 0.0 # Ini akan menjadi tahunan atau bulanan tergantung mode
    is_bunga_konstan_tahunan = False # Flag untuk fungsi hitung_pertumbuhan_bulanan

    if ubah_bunga:
        st.sidebar.subheader("Jadwal Bunga Berubah")
        st.sidebar.info("Masukkan **Bulan Mulai (ke-)** dan **Bunga Bulanan (%)** yang berlaku mulai bulan tersebut. Bulan 1 adalah bulan pertama simulasi.")

        default_jadwal_bunga = pd.DataFrame([
            {"Bulan Mulai": 1, "Bunga Bulanan (%)": 0.5},  # Default bunga bulanan 0.5% (6% per tahun)
            {"Bulan Mulai": 13, "Bunga Bulanan (%)": 0.7},
            {"Bulan Mulai": 25, "Bunga Bulanan (%)": 0.3},
        ])

        jadwal_bunga_persen = st.sidebar.data_editor(
            default_jadwal_bunga,
            num_rows="dynamic",
            column_config={
                "Bulan Mulai": st.column_config.NumberColumn(
                    "Bulan Mulai (ke-)", min_value=1, step=1, format="%d"
                ),
                "Bunga Bulanan (%)": st.column_config.NumberColumn( # Label diubah
                    "Bunga Bulanan (%)", min_value=-100.0, max_value=100.0, step=0.01, format="%.2f"
                ),
            },
            hide_index=True,
            key="jadwal_bunga_editor"
        )
        # Untuk tampilan ringkasan: ambil bunga bulanan pertama dari jadwal
        bunga_untuk_display_metric = jadwal_bunga_persen['Bunga Bulanan (%)'].iloc[0] if not jadwal_bunga_persen.empty else 0.0

    else: # Jika tidak diaktifkan, tampilkan input angka bunga tunggal (TAHUNAN)
        bunga_konstan_persen_for_calc = st.sidebar.number_input( # Variabel langsung dipakai untuk kalkulasi
            "Bunga Tahunan (%)", # Label diubah ke Tahunan
            min_value=0.0,
            max_value=100.0, # Bunga tahunan bisa lebih tinggi untuk kasus ekstrem
            value=5.0, # Default bunga tahunan 5%
            step=0.01,
            format="%.2f"
        )
        # Untuk tampilan ringkasan: gunakan nilai bunga tahunan yang diinput
        bunga_untuk_display_metric = bunga_konstan_persen_for_calc
        is_bunga_konstan_tahunan = True # Set flag ke True


    st.write(f"---")

    # --- Konten Sub-Mode Simulasi Pertumbuhan (tampilan di area utama) ---
    if mode_simulasi_sub == "Simulasi Pertumbuhan":
        durasi_bulan_simulasi = st.sidebar.number_input(
            "Durasi Simulasi (Bulan)",
            min_value=1,
            max_value=360,
            value=120, # Default 10 tahun
            step=1,
            format="%d"
        )
         
        st.write(f"---")

        st.subheader("Ringkasan Input Anda:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Uang Awal", format_rupiah(jumlah_awal))
        with col2:
            if ubah_bunga:
                st.metric("Bunga", "Lihat Jadwal")
            else:
                st.metric("Bunga Tahunan", f"{bunga_untuk_display_metric:.2f}%") # Label sesuai mode
        with col3:
            st.metric("Durasi", f"{durasi_bulan_simulasi} Bulan")


        st.write(f"---")

        # Tombol untuk menjalankan simulasi
        if st.sidebar.button("Jalankan Simulasi"):
            status_placeholder = st.empty()
            status_placeholder.info("Simulasi sedang berjalan...")

            # Persiapan parameter untuk hitung_pertumbuhan_bulanan
            if ubah_bunga:
                if jadwal_bunga_persen.empty:
                    status_placeholder.error("Mohon masukkan setidaknya satu entri di jadwal bunga berubah-ubah.")
                    st.stop()
                jadwal_bunga_for_calc = jadwal_bunga_persen.sort_values(by="Bulan Mulai").to_dict(orient='records')
                bunga_konstan_arg = 0.0 # Tidak digunakan dalam mode ini
                is_bunga_tahunan_arg = False # Bunga dari jadwal adalah bulanan
            else:
                jadwal_bunga_for_calc = None # Tidak ada jadwal
                bunga_konstan_arg = bunga_konstan_persen_for_calc # Bunga tahunan konstan
                is_bunga_tahunan_arg = True # Bunga konstan adalah tahunan
             
            data_pertumbuhan_bulanan = hitung_pertumbuhan_bulanan(
                jumlah_awal,
                jadwal_bunga_for_calc,
                durasi_bulan_simulasi,
                bunga_konstan_arg,
                is_bunga_tahunan_arg,
                start_date
            )
             
            if jumlah_awal == 0:
                is_all_bunga_zero = False
                if ubah_bunga and jadwal_bunga_persen is not None:
                    is_all_bunga_zero = all(float(item['Bunga Bulanan (%)']) == 0 for item in jadwal_bunga_persen.to_dict(orient='records'))
                elif not ubah_bunga and bunga_konstan_persen_for_calc == 0: 
                    is_all_bunga_zero = True
                 
                if is_all_bunga_zero:
                    for item in data_pertumbuhan_bulanan:
                        item['Jumlah Uang (Rp)'] = 0.0

            status_placeholder.empty()
            st.success("Simulasi Selesai!")

            st.subheader("Visualisasi Pertumbuhan Tabungan")
            fig, ax = plt.subplots(figsize=(12, 7))

            line_color = "#FF69B4"
            fill_color = "#FFC0CB"
             
            jumlah_uang_plot = [entry['Jumlah Uang (Rp)'] for entry in data_pertumbuhan_bulanan]
            tanggal_label_plot = [entry['Tanggal'] for entry in data_pertumbuhan_bulanan]
            x_ticks_positions = np.arange(len(data_pertumbuhan_bulanan))

            ax.plot(x_ticks_positions, jumlah_uang_plot, marker='o', linestyle='-', color=line_color, linewidth=2)
            ax.fill_between(x_ticks_positions, jumlah_uang_plot, color=fill_color, alpha=0.4)

            ax.set_title("Pertumbuhan Uang di Tabungan dari Waktu ke Waktu", fontsize=20, color="#2F4F4F")
            ax.set_xlabel("Tanggal", fontsize=16, color="#2F4F4F")
            ax.set_ylabel("Jumlah Uang (Rp)", fontsize=16, color="#2F4F4F")
            ax.grid(True, linestyle='--', alpha=0.7, color="#D3D3D3")
             
            step_for_ticks = 1
            if durasi_bulan_simulasi > 12:
                step_for_ticks = 6
            if durasi_bulan_simulasi > 60:
                step_for_ticks = 12
            if durasi_bulan_simulasi > 180:
                step_for_ticks = 24


            ax.set_xticks(x_ticks_positions[::step_for_ticks])
            ax.set_xticklabels(tanggal_label_plot[::step_for_ticks], rotation=45, ha='right', fontsize=10)


            ax.tick_params(axis='x', colors="#2F4F4F", labelsize=12)
            ax.tick_params(axis='y', colors="#2F4F4F", labelsize=12)

            def rupiah_formatter(x, p):
                return format_rupiah(x).replace("Rp ", "")

            formatter = plt.FuncFormatter(rupiah_formatter)
            ax.yaxis.set_major_formatter(formatter)

            jumlah_akhir = jumlah_uang_plot[-1]
             
            x_annotate_pos = x_ticks_positions[-1]
            y_annotate_pos = jumlah_uang_plot[-1]
             
            ax.annotate(f'Nilai Akhir: {format_rupiah(jumlah_akhir)}',
                        xy=(x_annotate_pos, y_annotate_pos),
                        xytext=(30, 30), # Offset 30 points ke kanan dan 30 points ke atas
                        textcoords='offset points', # Penting: membuat xytext sebagai offset
                        arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                        fontsize=14,
                        color='darkgreen',
                        ha='left', # Anotasi teks akan rata kiri dari titik xytext
                        va='bottom') # Anotasi teks akan rata bawah dari titik xytext

            fig.patch.set_facecolor("#FFF0F5")
            ax.set_facecolor("#FFFFFF")
            plt.tight_layout()

            st.pyplot(fig)
            plt.close(fig) # Menutup figure untuk membebaskan memori Matplotlib

            st.write("---")

            st.subheader("Detail Pertumbuhan Uang per Bulan")
            df_results = pd.DataFrame(data_pertumbuhan_bulanan)
            df_results['Jumlah Uang (Rp)'] = df_results['Jumlah Uang (Rp)'].apply(format_rupiah)
            st.dataframe(df_results, use_container_width=True)

            st.write("---")
            st.info("Catatan: Perhitungan ini mengasumsikan bunga majemuk berkelanjutan (continuous compounding) yang diterapkan secara bulanan.")


    # --- KONTEN SUB-MODE CARI DURASI TARGET (tampilan di area utama) ---
    elif mode_simulasi_sub == "Cari Durasi Target":
        st.sidebar.write("---")
        st.sidebar.subheader("Target Saldo & Durasi")
        target_jumlah = st.sidebar.number_input(
            "Target Jumlah Uang (Rp)",
            min_value=jumlah_awal,
            value=jumlah_awal * 1.5,
            step=100_000.0,
            format="%.2f",
            key="target_jumlah_input"
        )

        # Penentuan bunga estimasi untuk target, tergantung mode bunga
        bunga_estimasi_target = 0.0
        is_bunga_target_tahunan = False # Default untuk bunga berubah-ubah (bulanan)

        if ubah_bunga:
            st.sidebar.warning("Mode 'Cari Durasi Target' saat ini paling akurat untuk Bunga Konstan.")
            st.sidebar.info("Jika Bunga Berubah-ubah diaktifkan, perhitungan ini akan menggunakan bunga **bulanan** yang berlaku di Bulan 1 sebagai perkiraan rata-rata.") 
             
            if jadwal_bunga_persen is not None and not jadwal_bunga_persen.empty:
                # Ambil bunga bulanan dari jadwal, prioritaskan Bulan 1
                if 1 in jadwal_bunga_persen['Bulan Mulai'].values:
                    bunga_estimasi_target = jadwal_bunga_persen.loc[jadwal_bunga_persen['Bulan Mulai'] == 1, 'Bunga Bulanan (%)'].iloc[0]
                else:
                    bunga_estimasi_target = jadwal_bunga_persen.sort_values(by='Bulan Mulai')['Bunga Bulanan (%)'].iloc[0]
                is_bunga_target_tahunan = False # Bunga estimasi adalah bulanan
            else:
                bunga_estimasi_target = 0.0 # Default jika jadwal kosong
        else: # Mode Bunga Konstan (Tahunan)
            bunga_estimasi_target = bunga_konstan_persen_for_calc # Menggunakan bunga tahunan konstan
            is_bunga_target_tahunan = True # Bunga estimasi adalah tahunan

        if st.sidebar.button("Cari Durasi"):
            if bunga_estimasi_target <= 0:
                st.error("Bunga harus lebih besar dari 0% untuk mencapai target (tanpa dana tambahan).")
            elif jumlah_awal >= target_jumlah:
                st.success("Target sudah tercapai atau saldo awal sudah lebih besar!")
            else:
                hasil_durasi = hitung_durasi_target(
                    jumlah_awal,
                    target_jumlah,
                    bunga_estimasi_target, 
                    is_bunga_target_tahunan,
                    start_date
                )
                 
                if isinstance(hasil_durasi, tuple):
                    durasi_bulan_int, target_date = hasil_durasi
                    bunga_satuan_teks = "tahunan" if is_bunga_target_tahunan else "bulanan"
                    st.success(f"Untuk mencapai target {format_rupiah(target_jumlah)} dari {format_rupiah(jumlah_awal)} dengan bunga {bunga_estimasi_target:.2f}% per {bunga_satuan_teks}, dibutuhkan waktu sekitar **{durasi_bulan_int} bulan**.") 
                    st.write(f"Target diperkirakan akan tercapai pada **{target_date.strftime('%d %B %Y')}**.")
                else:
                    st.error(hasil_durasi)


# --- KONTEN UNTUK MODE PANDUAN PENGGUNA ---
elif mode_aplikasi_utama == "Panduan Penggunaan":
    st.header("📚 Panduan Penggunaan Sistem")
    st.markdown("""
   
    ### 1. Mode Sistem

    Di sidebar (sisi kiri), Anda akan menemukan 2 pilihan mode utama:

    * **Panduan Penggunaan:** Halaman ini, tempat Anda menemukan informasi cara menggunakan sistem.
    * **Mulai Simulasi:** Ini adalah mode interaktif utama untuk menjalankan simulasi pertumbuhan atau mencari durasi target.

    ### 2. Pengaturan Simulasi (dalam Mode 'Mulai Simulasi')

    Saat Anda memilih mode **'Mulai Simulasi'**, sidebar akan menampilkan pengaturan berikut:

    * **Pilih Sub-Mode Simulasi:**
        * **Simulasi Pertumbuhan:** Untuk melihat grafik dan tabel pertumbuhan uang Anda selama durasi tertentu.
        * **Cari Durasi Target:** Untuk menghitung berapa lama waktu yang Anda butuhkan untuk mencapai target saldo yang Anda inginkan.
    * **Jumlah Uang Awal (Rp):** Masukkan jumlah uang awal yang ingin Anda simulasikan.
    * **Tanggal Mulai Simulasi:** Tentukan tanggal kapan simulasi ini dimulai. Hasil tabel dan grafik akan mengikuti tanggal ini.
    * **Aktifkan Bunga Berubah-ubah:**
        * Jika **tidak dicentang:** Anda akan menggunakan **satu nilai bunga tahunan konstan** sepanjang simulasi. Masukkan nilai bunga tahunan (dalam %) di kolom yang tersedia.
        * Jika **dicentang:** Anda dapat membuat **jadwal bunga yang berubah-ubah** per bulan. Masukkan 'Bulan Mulai (ke-)' (nomor bulan ke-berapa simulasi berjalan, dimulai dari 1) dan 'Bunga Bulanan (%)' yang berlaku dari bulan tersebut. Anda dapat menambah atau menghapus baris jadwal.

    ### 3. Menjalankan Simulasi / Mencari Durasi

    Setelah semua parameter diisi sesuai mode yang dipilih:

    * Jika di sub-mode **'Simulasi Pertumbuhan'**: Atur 'Durasi Simulasi (Bulan)', lalu klik tombol **"Jalankan Simulasi"**.
    * Jika di sub-mode **'Cari Durasi Target'**: Masukkan 'Target Jumlah Uang (Rp)', lalu klik tombol **"Cari Durasi"**.

    ### 4. Memahami Hasil

    * **Ringkasan Input Anda:** Menampilkan kembali parameter yang Anda masukkan.
    * **Visualisasi Grafik:** Menunjukkan bagaimana saldo Anda tumbuh secara visual. Sumbu X adalah 'Tanggal', dan sumbu Y adalah 'Jumlah Uang (Rp)'. Titik 'Nilai Akhir' akan menunjukkan saldo akhir Anda.
    * **Detail Pertumbuhan Uang per Bulan:** Menampilkan tabel rinci saldo Anda untuk setiap bulan simulasi.
    * **Estimasi Durasi Target:** Jika di mode 'Cari Durasi Target', sistem akan menampilkan jumlah bulan yang dibutuhkan dan tanggal perkiraan target akan tercapai.

    ---
    """)


# --- Credit / Copyright (DITEMPATKAN DI SINI, DI LUAR IF/ELSE UTAMA) ---
st.write("---")
st.markdown(
    """
    <div style="text-align: center; font-size: 0.8em; color: #808080;">
        &copy; Neltriana Syafira - 2025
        <br>
        Dibuat sebagai proyek Persamaan Diferensial.
    </div>
    """,
    unsafe_allow_html=True
)