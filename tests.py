import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi database
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "db_demografi"

# Fungsi untuk mengambil data jenis kelamin
def get_gender_data():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            `Jenis Kelamin`, COUNT(*) AS jumlah
        FROM tb_demografi
        GROUP BY `Jenis Kelamin`
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fungsi untuk mengambil data agama
def get_religion_data():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            `Agama`, COUNT(*) AS jumlah
        FROM tb_demografi
        GROUP BY `Agama`
        ORDER BY jumlah DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fungsi untuk mengambil data pendidikan terakhir
def get_education_data():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            `Pendidikan Terakhir`, COUNT(*) AS jumlah
        FROM tb_demografi
        GROUP BY `Pendidikan Terakhir`
        ORDER BY jumlah DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fungsi untuk mengambil data pendidikan berdasarkan usia dengan filter kategori yang valid
def get_education_by_age():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            CASE 
                WHEN Umur BETWEEN 0 AND 5 THEN 'Pra Sekolah'
                WHEN Umur BETWEEN 6 AND 12 THEN 'SD'
                WHEN Umur BETWEEN 13 AND 15 THEN 'SMP'
                WHEN Umur BETWEEN 16 AND 18 THEN 'SMA'
                ELSE NULL  -- Kategori lain akan diabaikan
            END AS Kategori_Usia,
            COUNT(*) AS jumlah
        FROM tb_demografi
        WHERE Umur BETWEEN 0 AND 18  -- Memastikan hanya mengambil data dalam rentang ini
        GROUP BY Kategori_Usia
        ORDER BY jumlah DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Hapus kategori NULL (data yang tidak sesuai kriteria)
    df = df.dropna()

    return df

# Fungsi untuk mengambil data pekerjaan
def get_job_data():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            `PEKERJAAN FIX` AS Pekerjaan, COUNT(*) AS jumlah
        FROM tb_demografi
        GROUP BY `PEKERJAAN FIX`
        ORDER BY jumlah DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fungsi untuk mengambil data distribusi usia
def get_age_distribution():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            CASE 
                WHEN Umur BETWEEN 0 AND 20 THEN '0-20 Tahun'
                WHEN Umur BETWEEN 21 AND 40 THEN '21-40 Tahun'
                WHEN Umur BETWEEN 41 AND 60 THEN '41-60 Tahun'
                WHEN Umur BETWEEN 61 AND 80 THEN '61-80 Tahun'
                WHEN Umur >= 81 THEN 'Diatas 81 Tahun'
                ELSE NULL  -- Kategori lain akan diabaikan
            END AS Kategori_Usia,
            COUNT(*) AS jumlah
        FROM tb_demografi
        WHERE Umur IS NOT NULL  -- Pastikan umur tidak kosong
        GROUP BY Kategori_Usia
        ORDER BY jumlah DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # # Hapus kategori NULL (data yang tidak sesuai kriteria)
    # df = df.dropna()

    return df

# Fungsi untuk mengambil data distribusi pendapatan keluarga berdasarkan No KK
def get_income_distribution():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            CASE 
                WHEN `Pendapatan Rata-rata keluarga dalam satu Bulan (6 Bulan terakhir` < 1000000 THEN 'Dibawah 1 Juta'
                WHEN `Pendapatan Rata-rata keluarga dalam satu Bulan (6 Bulan terakhir` BETWEEN 1000000 AND 4000000 THEN '1 Juta - 4 Juta'
                WHEN `Pendapatan Rata-rata keluarga dalam satu Bulan (6 Bulan terakhir` > 4000000 THEN 'Diatas 4 Juta'
            END AS Kategori_Pendapatan,
            COUNT(DISTINCT `No KK`) AS jumlah_KK  -- Memastikan hanya menghitung KK unik
        FROM tb_demografi
        WHERE `Pendapatan Rata-rata keluarga dalam satu Bulan (6 Bulan terakhir` IS NOT NULL
        GROUP BY Kategori_Pendapatan
        ORDER BY jumlah_KK DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Hapus kategori NULL (data yang tidak sesuai kriteria)
    df = df.dropna()

    return df

# Fungsi untuk mengambil data distribusi pengeluaran keluarga berdasarkan No KK
def get_expenditure_distribution():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            CASE 
                WHEN `Pengeluaran Rata-Rata keluarga dalam satu bulan` < 1000000 THEN 'Dibawah 1 Juta'
                WHEN `Pengeluaran Rata-Rata keluarga dalam satu bulan` BETWEEN 1000000 AND 4000000 THEN '1 Juta - 4 Juta'
                WHEN `Pengeluaran Rata-Rata keluarga dalam satu bulan` > 4000000 THEN 'Diatas 4 Juta'
                ELSE NULL  -- Kategori lain akan diabaikan
            END AS Kategori_Pengeluaran,
            COUNT(DISTINCT `No KK`) AS jumlah_KK  -- Menghitung jumlah KK unik
        FROM tb_demografi
        WHERE `Pengeluaran Rata-Rata keluarga dalam satu bulan` IS NOT NULL
        GROUP BY Kategori_Pengeluaran
        ORDER BY jumlah_KK DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Hapus kategori NULL (data yang tidak sesuai kriteria)
    df = df.dropna()

    return df

# Fungsi untuk mengambil data disabilitas
def get_disability_distribution():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            `Disabilitas` AS Status_Difabel,
            COUNT(*) AS jumlah
        FROM tb_demografi
        WHERE `Disabilitas` IS NOT NULL  -- Pastikan data tidak kosong
        GROUP BY `Disabilitas`
        ORDER BY jumlah DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    return df

# -- Fungsi untuk mengambil data minat pelatihan gabungan --
def get_training_interest():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            Pelatihan,
            COUNT(*) AS jumlah
        FROM
        (
            SELECT `Pelatihan Diminati I` AS Pelatihan
            FROM tb_demografi
            WHERE `Pelatihan Diminati I` IS NOT NULL

            UNION ALL

            SELECT `Pelatihan Diminati II`
            FROM tb_demografi
            WHERE `Pelatihan Diminati II` IS NOT NULL

            UNION ALL

            SELECT `Pelatihan Diminati III`
            FROM tb_demografi
            WHERE `Pelatihan Diminati III` IS NOT NULL
        ) AS sub
        WHERE Pelatihan IN (
            'Memasak', 
            'Kelistrikan', 
            'Menyetir', 
            'Menjahit', 
            'Pertukangan', 
            'Salon', 
            'Design & Sablon', 
            'Pijat Urut', 
            'Membatik'
            -- Tambahkan kategori lain jika ada
        )
        GROUP BY Pelatihan
        ORDER BY jumlah DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Hapus kategori NULL (data yang tidak sesuai kriteria)
    df = df.dropna()

    return df

# Fungsi untuk mengambil data millennial dan non-millennial
def get_millennial_distribution():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            `Milenial/Non Milenial` AS Kategori,
            COUNT(*) AS jumlah
        FROM tb_demografi
        WHERE `Milenial/Non Milenial` IS NOT NULL  -- Pastikan data tidak kosong
        GROUP BY `Milenial/Non Milenial`
        ORDER BY jumlah DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    return df

# Fungsi untuk mengambil data KK milenial dan non-milenial berdasarkan No KK
def get_kk_millennial_distribution():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    query = """
        SELECT 
            `Milenial/Non Milenial` AS Kategori,
            COUNT(DISTINCT `No KK`) AS jumlah_KK
        FROM tb_demografi
        WHERE `Milenial/Non Milenial` IS NOT NULL  -- Pastikan data tidak kosong
        GROUP BY `Milenial/Non Milenial`
        ORDER BY jumlah_KK DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    return df

# --- TAMPILKAN JUDUL ---
st.title("Dashboard Demografi Rusun")

# --- VISUALISASI JENIS KELAMIN ---
st.subheader("Distribusi Jenis Kelamin")

df_gender = get_gender_data()

if len(df_gender) == 2:
    total_populasi = df_gender["jumlah"].sum()
    persen_laki = (df_gender.loc[df_gender["Jenis Kelamin"] == "Laki-Laki", "jumlah"].values[0] / total_populasi) * 100
    persen_perempuan = (df_gender.loc[df_gender["Jenis Kelamin"] == "Perempuan", "jumlah"].values[0] / total_populasi) * 100

    colors = ["blue", "red"]
    labels = [f"Laki-laki {persen_laki:.2f}%", f"Perempuan {persen_perempuan:.2f}%"]
    sizes = [persen_laki, persen_perempuan]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts = ax.pie(
        sizes, labels=labels, startangle=90, colors=colors, wedgeprops={"edgecolor": "black"},
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )

    plt.text(0, 0, f"{total_populasi:,.0f}\nJiwa", fontsize=16, fontweight="bold", ha="center", va="center")
    st.pyplot(fig)
else:
    st.write("Data tidak lengkap atau tidak memiliki dua kategori gender.")

# --- VISUALISASI AGAMA ---
st.subheader("Distribusi Agama")

df_agama = get_religion_data()

if not df_agama.empty:
    total_populasi = df_agama["jumlah"].sum()
    df_agama = df_agama.sort_values(by="jumlah", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(y=df_agama["Agama"], x=df_agama["jumlah"], palette="Oranges_r", ax=ax)

    for index, value in enumerate(df_agama["jumlah"]):
        ax.text(value + 500, index, f"{value:,.0f}", fontsize=12, va="center", fontweight="bold", color="black")

    ax.set_title("Distribusi Agama", fontsize=14, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")
    st.pyplot(fig)

    st.subheader("Persentase Agama")
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = sns.color_palette("pastel", len(df_agama))
    ax.pie(df_agama["jumlah"], labels=df_agama["Agama"], autopct="%1.1f%%", colors=colors, startangle=90, wedgeprops={"edgecolor": "black"})
    
    plt.title("Persentase Agama", fontsize=14, fontweight="bold")
    st.pyplot(fig)
else:
    st.write("Data agama tidak tersedia.")

# --- VISUALISASI PENDIDIKAN TERAKHIR ---
st.subheader("Distribusi Pendidikan Terakhir")

df_pendidikan = get_education_data()

if not df_pendidikan.empty:
    total_populasi = df_pendidikan["jumlah"].sum()
    df_pendidikan = df_pendidikan.sort_values(by="jumlah", ascending=False)

    colors = sns.color_palette("coolwarm", len(df_pendidikan))

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        df_pendidikan["jumlah"], labels=df_pendidikan["Pendidikan Terakhir"], autopct='%1.2f%%', 
        colors=colors, startangle=140, wedgeprops={"edgecolor": "black"},
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )

    plt.text(0, 0, f"{total_populasi:,.0f}\nJiwa", fontsize=16, fontweight="bold", ha="center", va="center")
    plt.title("Persentase Pendidikan Terakhir", fontsize=14, fontweight="bold")
    st.pyplot(fig)
else:
    st.write("Data pendidikan tidak tersedia.")

# --- VISUALISASI PENDIDIKAN BERDASARKAN USIA ---
st.subheader("Distribusi Pendidikan Berdasarkan Usia")

df_pendidikan_usia = get_education_by_age()

if not df_pendidikan_usia.empty:
    total_populasi = df_pendidikan_usia["jumlah"].sum()

    colors = sns.color_palette("coolwarm", len(df_pendidikan_usia))

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        df_pendidikan_usia["jumlah"], labels=df_pendidikan_usia["Kategori_Usia"], autopct='%1.0f%%', 
        colors=colors, startangle=140, wedgeprops={"edgecolor": "black"},
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )

    plt.text(0, 0, f"{total_populasi:,.0f}\nJiwa", fontsize=16, fontweight="bold", ha="center", va="center")
    plt.title("Pendidikan Berdasarkan Usia", fontsize=14, fontweight="bold")
    st.pyplot(fig)
else:
    st.write("Data pendidikan berdasarkan usia tidak tersedia atau tidak sesuai kriteria.")

# --- VISUALISASI PEKERJAAN ---
st.subheader("Distribusi Pekerjaan")

df_pekerjaan = get_job_data()

if not df_pekerjaan.empty:
    total_pekerja = df_pekerjaan["jumlah"].sum()

    # Urutkan dari jumlah terbanyak ke terkecil
    df_pekerjaan = df_pekerjaan.sort_values(by="jumlah", ascending=True)

    # Buat Bar Chart Horizontal
    fig, ax = plt.subplots(figsize=(10, 12))
    bars = ax.barh(df_pekerjaan["Pekerjaan"], df_pekerjaan["jumlah"], color="royalblue")

    # Tambahkan label jumlah di samping setiap bar
    for bar, value in zip(bars, df_pekerjaan["jumlah"]):
        ax.text(value + 100, bar.get_y() + bar.get_height()/2, f"{value:,.0f}", 
                fontsize=10, va="center", fontweight="bold", color="black")

    # Tambahkan judul dan format tampilan
    ax.set_title("Distribusi Pekerjaan", fontsize=14, fontweight="bold")
    ax.set_xlabel("Jumlah", fontsize=12)
    ax.set_ylabel("")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Tampilkan di Streamlit
    st.pyplot(fig)

else:
    st.write("Data pekerjaan tidak tersedia.")

# --- VISUALISASI DISTRIBUSI USIA ---
st.subheader("Distribusi Usia Penduduk")

df_usia = get_age_distribution()

if not df_usia.empty:
    total_populasi = df_usia["jumlah"].sum()

    # Warna-warna untuk pie chart
    colors = sns.color_palette("coolwarm", len(df_usia))

    # Efek explode untuk kategori kecil agar lebih menonjol
    explode = [0.05 if p < 5 else 0 for p in df_usia["jumlah"] / total_populasi * 100]

    # Buat Pie Chart Distribusi Usia
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        df_usia["jumlah"], labels=df_usia["Kategori_Usia"], autopct='%1.0f%%', 
        colors=colors, startangle=140, explode=explode, wedgeprops={"edgecolor": "black"},
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )

    # Tambahkan teks di tengah lingkaran
    plt.text(0, 0, f"{total_populasi:,.0f}\nJiwa", fontsize=16, fontweight="bold", ha="center", va="center")

    # Tambahkan judul
    plt.title("Distribusi Usia Penduduk", fontsize=14, fontweight="bold")

    # Tampilkan di Streamlit
    st.pyplot(fig)
    
else:
    st.write("Data usia tidak tersedia atau tidak sesuai kriteria.")

# --- VISUALISASI DISTRIBUSI PENDAPATAN ---
st.subheader("Distribusi Pendapatan Keluarga")

df_pendapatan = get_income_distribution()

# # **Pastikan nama kolom sebelum menggunakannya**
# st.write("Kolom yang tersedia dalam df_pendapatan:", df_pendapatan.columns.tolist())

if not df_pendapatan.empty:
    total_keluarga = df_pendapatan["jumlah_KK"].sum()  # Menggunakan nama kolom yang benar

    # Warna-warna untuk pie chart
    colors = sns.color_palette("coolwarm", len(df_pendapatan))

    # Efek explode untuk kategori kecil agar lebih menonjol
    explode = [0.05 if p < 10 else 0 for p in df_pendapatan["jumlah_KK"] / total_keluarga * 100]

    # Buat Pie Chart Distribusi Pendapatan
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        df_pendapatan["jumlah_KK"], labels=df_pendapatan["Kategori_Pendapatan"], autopct='%1.0f%%', 
        colors=colors, startangle=140, explode=explode, wedgeprops={"edgecolor": "black"},
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )

    # Tambahkan teks di tengah lingkaran
    plt.text(0, 0, f"{total_keluarga:,.0f}\nKK", fontsize=16, fontweight="bold", ha="center", va="center")

    # Tambahkan judul
    plt.title("Distribusi Pendapatan Keluarga", fontsize=14, fontweight="bold")

    # Tampilkan di Streamlit
    st.pyplot(fig)
    
else:
    st.write("Data pendapatan tidak tersedia atau tidak sesuai kriteria.")

# --- VISUALISASI DISTRIBUSI PENGELUARAN ---
st.subheader("Distribusi Pengeluaran Keluarga")

df_pengeluaran = get_expenditure_distribution()

if not df_pengeluaran.empty:
    total_keluarga = df_pengeluaran["jumlah_KK"].sum()

    # Warna-warna untuk pie chart
    colors = sns.color_palette("coolwarm", len(df_pengeluaran))

    # Efek explode untuk kategori kecil agar lebih menonjol
    explode = [0.05 if p < 10 else 0 for p in df_pengeluaran["jumlah_KK"] / total_keluarga * 100]

    # Buat Pie Chart Distribusi Pengeluaran
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        df_pengeluaran["jumlah_KK"], labels=df_pengeluaran["Kategori_Pengeluaran"], autopct='%1.0f%%', 
        colors=colors, startangle=140, explode=explode, wedgeprops={"edgecolor": "black"},
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )

    # Tambahkan teks di tengah lingkaran
    plt.text(0, 0, f"{total_keluarga:,.0f}\nKK", fontsize=16, fontweight="bold", ha="center", va="center")

    # Tambahkan judul
    plt.title("Distribusi Pengeluaran Keluarga", fontsize=14, fontweight="bold")

    # Tampilkan di Streamlit
    st.pyplot(fig)
    
else:
    st.write("Data pengeluaran tidak tersedia atau tidak sesuai kriteria.")

# --- VISUALISASI DISABILITAS ---
st.subheader("Distribusi Penduduk Difabel")

df_difabel = get_disability_distribution()

if not df_difabel.empty:
    total_populasi = df_difabel["jumlah"].sum()

    # Warna-warna untuk pie chart
    colors = ["#f4a261", "#264653"]  # Warna oranye & biru gelap

    # Efek explode untuk kategori kecil agar lebih menonjol
    explode = [0.1 if label == "Ya" else 0 for label in df_difabel["Status_Difabel"]]

    # Buat Pie Chart Distribusi Difabel
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        df_difabel["jumlah"], labels=df_difabel["Status_Difabel"], autopct='%1.2f%%', 
        colors=colors, startangle=90, explode=explode, wedgeprops={"edgecolor": "black"},
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )

    # Tambahkan teks di tengah lingkaran
    plt.text(0, 0, f"{total_populasi:,.0f}\nJiwa", fontsize=16, fontweight="bold", ha="center", va="center")

    # Tambahkan judul
    plt.title("Distribusi Penduduk Difabel", fontsize=14, fontweight="bold")

    # Tampilkan di Streamlit
    st.pyplot(fig)
    
else:
    st.write("Data disabilitas tidak tersedia atau tidak sesuai kriteria.")

# -- VISUALISASI MINAT PELATIHAN (GABUNGAN) --
st.subheader("Distribusi Minat Pelatihan (I, II, III)")

df_pelatihan = get_training_interest()

if not df_pelatihan.empty:
    total_peminat = df_pelatihan["jumlah"].sum()

    # Warna untuk pie chart (seaborn color palette)
    colors = sns.color_palette("coolwarm", len(df_pelatihan))

    # Efek explode untuk kategori kecil agar lebih menonjol
    # Contoh: explode jika < 5% total
    explode = [0.05 if (row_jml/total_peminat*100) < 5 else 0 for row_jml in df_pelatihan["jumlah"]]

    # Buat Pie Chart
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        df_pelatihan["jumlah"], 
        labels=df_pelatihan["Pelatihan"], 
        autopct='%1.2f%%', 
        colors=colors, 
        startangle=140, 
        explode=explode, 
        wedgeprops={"edgecolor": "black"},
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )

    # Tampilkan total di tengah lingkaran
    plt.text(0, 0, f"{total_peminat:,.0f}\nJiwa", 
             fontsize=16, fontweight="bold", ha="center", va="center")

    plt.title("Distribusi Minat Pelatihan (Gabungan I, II, III)", 
              fontsize=14, fontweight="bold")
    
    st.pyplot(fig)
else:
    st.write("Data minat pelatihan (I, II, III) tidak tersedia atau tidak sesuai kriteria.")

# --- VISUALISASI MILENIAL vs NON-MILENIAL ---
st.subheader("Distribusi Millennial dan Non-Millennial")

df_millennial = get_millennial_distribution()

if not df_millennial.empty:
    total_populasi = df_millennial["jumlah"].sum()

    # Warna untuk pie chart (seaborn color palette)
    colors = ["#f4a261", "#2a9d8f"]  # Oranye untuk Non-Millennial, Biru untuk Millennial

    # Efek explode untuk kategori kecil agar lebih menonjol
    explode = [0.05 if kategori == "Millennial" else 0 for kategori in df_millennial["Kategori"]]

    # Buat Pie Chart
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        df_millennial["jumlah"], 
        labels=df_millennial["Kategori"], 
        autopct='%1.2f%%', 
        colors=colors, 
        startangle=90, 
        explode=explode, 
        wedgeprops={"edgecolor": "black"},
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )

    # Tampilkan total populasi di tengah lingkaran
    plt.text(0, 0, f"{total_populasi:,.0f}\nJiwa", 
             fontsize=16, fontweight="bold", ha="center", va="center")

    plt.title("Distribusi Millennial dan Non-Millennial", 
              fontsize=14, fontweight="bold")
    
    st.pyplot(fig)
else:
    st.write("Data Millennial/Non-Millennial tidak tersedia atau tidak sesuai kriteria.")

# --- VISUALISASI KK MILENIAL vs NON-MILENIAL ---
st.subheader("Distribusi KK Milenial dan Non-Milenial")

df_kk_millennial = get_kk_millennial_distribution()

if not df_kk_millennial.empty:
    total_kk = df_kk_millennial["jumlah_KK"].sum()

    # Warna untuk pie chart (seaborn color palette)
    colors = ["#2a9d8f", "#50c2c9"]  # Warna gradasi biru untuk tampilan menarik

    # Efek explode untuk kategori kecil agar lebih menonjol
    explode = [0.05 if kategori == "Millennial" else 0 for kategori in df_kk_millennial["Kategori"]]

    # Buat Pie Chart
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        df_kk_millennial["jumlah_KK"], 
        labels=df_kk_millennial["Kategori"], 
        autopct='%1.2f%%', 
        colors=colors, 
        startangle=90, 
        explode=explode, 
        wedgeprops={"edgecolor": "black"},
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )

    # Tampilkan total KK di tengah lingkaran
    plt.text(0, 0, f"{total_kk:,.0f}\nKK", 
             fontsize=16, fontweight="bold", ha="center", va="center")

    plt.title("Distribusi KK Milenial dan Non-Milenial", 
              fontsize=14, fontweight="bold")
    
    st.pyplot(fig)
else:
    st.write("Data KK Milenial/Non-Milenial tidak tersedia atau tidak sesuai kriteria.")

