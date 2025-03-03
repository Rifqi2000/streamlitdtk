import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px

st.set_page_config(page_title="Dashboard", layout="wide")

# # Konfigurasi database
# DB_HOST = "localhost"
# DB_USER = "root"
# DB_PASSWORD = ""
# DB_NAME = "db_demografi"

DB_HOST = "192.168.40.160"
DB_USER = "admin"
DB_PASSWORD = ""
DB_NAME = "db_demografi"


def get_data(query):
    """Fungsi untuk mengambil data dari database dan menangani nilai kosong."""
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        df = pd.read_sql(query, conn)
        conn.close()
        return df if not df.empty else pd.DataFrame()
    except Exception as e:
        st.error(f"Error dalam mengambil data: {e}")
        return pd.DataFrame()

# Dropdown untuk memilih halaman
selected_page = st.sidebar.selectbox("Pilih Halaman", ["Demografi", "Tunggakan dan Kepemilikan"])

# --- Ambil daftar bulan langsung dari database ---
month_query = """
    SELECT DISTINCT upload_data AS bulan FROM tb_demografi ORDER BY bulan DESC
"""
df_months = get_data(month_query)

# --- Buat filter bulan ---
st.sidebar.header("📅 Filter Data")

if not df_months.empty:
    df_months = df_months.dropna().drop_duplicates()  # Pastikan tidak ada nilai NULL dan duplikasi
    
    # Pilihan dropdown untuk filter bulan
    selected_month = st.sidebar.selectbox("Pilih Bulan", ["Semua"] + df_months["bulan"].tolist())

    # Tentukan kondisi filter SQL
    if selected_month != "Semua":
        month_condition = f"AND upload_data = '{selected_month}'"
    else:
        month_condition = ""
else:
    st.sidebar.warning("⚠ Data bulan tidak tersedia.\nMenampilkan semua data.")
    month_condition = ""

# --- Tampilan Streamlit ---
if selected_page == "Demografi":
    st.title("📊 Dashboard Demografi Rusun")
elif selected_page == "Tunggakan dan Kepemilikan":
    st.title("📊 Dashboard Tunggakan dan Kepemilikan")
st.markdown("---")

# --- Layout dua kolom ---
col1, col2 = st.columns(2)

if selected_page == "Demografi":
    with col1:
        st.subheader("JENIS KELAMIN")

        # Pastikan kondisi WHERE benar
        query = f"""
            SELECT Jenis_Kelamin, COUNT(*) AS jumlah 
            FROM data_demografi 
            {"WHERE upload_data = '" + selected_month + "'" if selected_month != "Semua" else ""}
            GROUP BY Jenis_Kelamin
        """

        df_gender = get_data(query)

        if not df_gender.empty:
            fig = px.pie(df_gender, names='Jenis_Kelamin', values='jumlah', 
                        title="Persentase Jenis Kelamin", 
                        color_discrete_sequence=px.colors.sequential.Viridis)
            fig.update_layout(font=dict(size=18))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada data jenis kelamin yang tersedia untuk bulan yang dipilih.")
        
        # --- Perbaikan Query Pendidikan Terakhir ---
        st.subheader("PENDIDIKAN TERAKHIR")

        query = f"""
            SELECT 
                CASE 
                    WHEN Umur BETWEEN 0 AND 5 THEN 'Pra Sekolah'
                    WHEN Umur BETWEEN 6 AND 12 THEN 'SD'
                    WHEN Umur BETWEEN 13 AND 15 THEN 'SMP'
                    WHEN Umur BETWEEN 16 AND 18 THEN 'SMA'
                    ELSE NULL
                END AS Kategori_Usia, 
                COUNT(*) AS jumlah 
            FROM tb_demografi
            WHERE Umur BETWEEN 0 AND 18
            {month_condition}
            GROUP BY Kategori_Usia 
            ORDER BY jumlah DESC
        """

        df_pendidikan = get_data(query)

        if not df_pendidikan.empty:
            fig = px.pie(df_pendidikan, names='Kategori_Usia', values='jumlah', 
                        title="Persentase Pendidikan Terakhir", 
                        color_discrete_sequence=px.colors.sequential.Plasma)
            fig.update_layout(font=dict(size=18))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada data pendidikan yang tersedia untuk bulan yang dipilih.")
            
            st.subheader("PEKERJAAN")
            df_job = get_data(f"""
                SELECT `PEKERJAAN_FIX` AS Pekerjaan, COUNT(*) AS jumlah 
                FROM data_demografi 
                {month_condition} 
                GROUP BY `PEKERJAAN_FIX`
                ORDER BY jumlah ASC
            """)

            if not df_job.empty:
                fig = px.bar(df_job, x='jumlah', y='Pekerjaan', orientation='h', title="Distribusi Pekerjaan",
                            color='jumlah', color_continuous_scale=px.colors.sequential.Tealgrn)
                st.plotly_chart(fig, use_container_width=True)
                
        st.subheader("PENGHASILAN")
        df_income = get_data(f"""
            SELECT 
                CASE 
                    WHEN `Pendapatan_Rata_rata_Keluarga` < 1000000 THEN 'Dibawah 1 Juta'
                    WHEN `Pendapatan_Rata_rata_Keluarga` BETWEEN 1000000 AND 4000000 THEN '1 Juta - 4 Juta'
                    WHEN `Pendapatan_Rata_rata_Keluarga` > 4000000 THEN 'Diatas 4 Juta'
                END AS Kategori_Pendapatan,
                COUNT(DISTINCT `No_KK`) AS jumlah_KK
            FROM data_demografi
            WHERE `Pendapatan_Rata_rata_Keluarga` IS NOT NULL
            {month_condition}
            GROUP BY Kategori_Pendapatan
            ORDER BY jumlah_KK DESC
        """)

        if not df_income.empty:
            fig = px.pie(df_income, names='Kategori_Pendapatan', values='jumlah_KK',
                        title="Distribusi Penghasilan Keluarga", color_discrete_sequence=px.colors.sequential.Cividis)
            fig.update_layout(font=dict(size=18))
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("DISABILITAS")
        df_disability = get_data(f"""
            SELECT 
                `Disabilitas` AS Status_Difabel,
                COUNT(*) AS jumlah
            FROM data_demografi
            WHERE `Disabilitas` IS NOT NULL  -- Pastikan data tidak kosong
            {month_condition}
            GROUP BY `Disabilitas`
            ORDER BY jumlah DESC
        """)

        if not df_disability.empty:
            fig = px.pie(df_disability, names='Status_Difabel', values='jumlah', 
                        title="Distribusi Penduduk Difabel",
                        color_discrete_sequence=px.colors.sequential.Magenta)
            fig.update_layout(font=dict(size=18))
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("WARGA MILENIAL")

        df_millennial = get_data(f"""
            SELECT 
                `Milenial_Non_Milenial` AS Kategori,
                COUNT(*) AS jumlah
            FROM data_demografi
            WHERE `Milenial_Non_Milenial` IS NOT NULL  
            {month_condition}
            GROUP BY `Milenial_Non_Milenial`
            ORDER BY 
                CASE Kategori 
                    WHEN 'Milenial' THEN 1
                    WHEN 'NON Milenial' THEN 2
                    ELSE 3
                END
        """)

        if not df_millennial.empty:
            fig = px.pie(df_millennial, names='Kategori', values='jumlah',
                        title="Distribusi Warga Milenial", 
                        color_discrete_sequence=px.colors.sequential.Magenta)
            fig.update_layout(font=dict(size=18))
            st.plotly_chart(fig, use_container_width=True)

        
        st.subheader("JUMLAH JIWA PER UPRS")

        df_jiwa = get_data("""
            SELECT TRIM(UPRS) AS Nama_UPRS, COUNT(*) AS Total_Jiwa
            FROM data_demografi
            WHERE UPRS IS NOT NULL
            GROUP BY Nama_UPRS
        """)

        # **Pastikan nama kolom sesuai dengan hasil query**
        if "Nama_UPRS" not in df_jiwa.columns:
            st.warning("Kolom 'UPRS' tidak ditemukan dalam database.")
        else:
            # **Pastikan hanya UPRS I - VIII yang ada**
            urutan_uprs = ["UPRS I", "UPRS II", "UPRS III", "UPRS IV", "UPRS V", "UPRS VI", "UPRS VII", "UPRS VIII"]
            df_jiwa["Nama_UPRS"] = df_jiwa["Nama_UPRS"].astype(str).str.strip()  # Hapus spasi ekstra
            df_jiwa = df_jiwa[df_jiwa["Nama_UPRS"].isin(urutan_uprs)]

            # **Cek apakah data kosong setelah filter**
            if df_jiwa.empty:
                st.warning("Tidak ada data jiwa yang tersedia untuk UPRS I - VIII.")
            else:
                # **Pastikan urutan tetap dari UPRS I - VIII**
                df_jiwa["Nama_UPRS"] = pd.Categorical(df_jiwa["Nama_UPRS"], categories=urutan_uprs, ordered=True)
                df_jiwa = df_jiwa.sort_values("Nama_UPRS")

                # **Buat Visualisasi**
                fig = px.bar(df_jiwa, x="Nama_UPRS", y="Total_Jiwa", 
                            title="Jumlah Jiwa per UPRS (Urutan I - VIII)",
                            labels={"Total_Jiwa": "Jumlah Jiwa", "Nama_UPRS": "UPRS"},
                            color="Total_Jiwa", color_continuous_scale=px.colors.sequential.Oranges,
                            text_auto=True)
                fig.update_layout(font=dict(size=18))
                
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("AGAMA")

        # Pastikan kondisi WHERE benar
        query = f"""
            SELECT Agama, COUNT(*) AS jumlah 
            FROM data_demografi 
            {"WHERE upload_data = '" + selected_month + "'" if selected_month != "Semua" else ""}
            GROUP BY Agama 
            ORDER BY jumlah ASC
        """

        df_agama = get_data(query)

        if not df_agama.empty:
            fig = px.bar(df_agama, x='jumlah', y='Agama', orientation='h', 
                        title="Distribusi Agama", 
                        color='jumlah', 
                        color_continuous_scale=px.colors.sequential.Bluered_r,
                        text_auto=True)
            fig.update_layout(font=dict(size=12))
            
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada data agama yang tersedia untuk bulan yang dipilih.")

        
        st.subheader("PENDIDIKAN BERDASARKAN USIA")
        df_edu_age = get_data(f"""
            SELECT 
                CASE 
                    WHEN Umur BETWEEN 0 AND 5 THEN 'Pra Sekolah'
                    WHEN Umur BETWEEN 6 AND 12 THEN 'SD'
                    WHEN Umur BETWEEN 13 AND 15 THEN 'SMP'
                    WHEN Umur BETWEEN 16 AND 18 THEN 'SMA'
                    ELSE NULL  -- Kategori lain akan diabaikan
                END AS Kategori_Usia,
                COUNT(*) AS jumlah
            FROM data_demografi
            WHERE Umur BETWEEN 0 AND 18  
            {month_condition}
            GROUP BY Kategori_Usia
            ORDER BY jumlah DESC
        """)

        if not df_edu_age.empty:
            fig = px.pie(df_edu_age, names='Kategori_Usia', values='jumlah', 
                        title="Pendidikan Berdasarkan Usia",
                        color_discrete_sequence=px.colors.sequential.Sunset)
            fig.update_layout(font=dict(size=18))
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("USIA")

        # Perbaikan struktur WHERE agar tidak menyebabkan error
        query = f"""
            SELECT 
                CASE 
                    WHEN Umur BETWEEN 0 AND 20 THEN '0-20 Tahun'
                    WHEN Umur BETWEEN 21 AND 40 THEN '21-40 Tahun'
                    WHEN Umur BETWEEN 41 AND 60 THEN '41-60 Tahun'
                    WHEN Umur BETWEEN 61 AND 80 THEN '61-80 Tahun'
                    WHEN Umur >= 81 THEN 'Diatas 80 Tahun'
                    ELSE 'null'
                END AS Kategori_Usia, COUNT(*) AS jumlah 
            FROM data_demografi 
            WHERE Umur IS NOT NULL 
            {"AND upload_data = '" + selected_month + "'" if selected_month != "Semua" else ""}
            GROUP BY Kategori_Usia 
            ORDER BY 
                CASE Kategori_Usia 
                    WHEN '0-20 Tahun' THEN 1
                    WHEN '21-40 Tahun' THEN 2
                    WHEN '41-60 Tahun' THEN 3
                    WHEN '61-80 Tahun' THEN 4
                    WHEN 'Diatas 80 Tahun' THEN 5
                    ELSE 6
                END
        """

        df_usia = get_data(query)

        if not df_usia.empty:
            total_penduduk = df_usia['jumlah'].sum()
            df_usia['persentase'] = (df_usia['jumlah'] / total_penduduk) * 100

            fig = px.pie(df_usia, names='Kategori_Usia', values='persentase', 
                        title="Distribusi Usia Penduduk", 
                        color_discrete_sequence=px.colors.sequential.Tealgrn, 
                        hole=0.3)
            fig.update_layout(font=dict(size=18))
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada data usia yang tersedia untuk bulan yang dipilih.")


        
        st.subheader("PENGELUARAN")
        df_expenditure = get_data(f"""
            SELECT 
                CASE 
                    WHEN `Pengeluaran_Rata_Rata_Keluarga` < 1000000 THEN 'Dibawah 1 Juta'
                    WHEN `Pengeluaran_Rata_Rata_Keluarga` BETWEEN 1000000 AND 4000000 THEN '1 Juta - 4 Juta'
                    WHEN `Pengeluaran_Rata_Rata_Keluarga` > 4000000 THEN 'Diatas 4 Juta'
                    ELSE NULL  
                END AS Kategori_Pengeluaran,
                COUNT(DISTINCT `No_KK`) AS jumlah_KK  
            FROM data_demografi
            WHERE `Pengeluaran_Rata_Rata_Keluarga` IS NOT NULL
            {month_condition}
            GROUP BY Kategori_Pengeluaran
            ORDER BY jumlah_KK DESC
        """)

        if not df_expenditure.empty:
            fig = px.pie(df_expenditure, names='Kategori_Pengeluaran', values='jumlah_KK',
                        title="Distribusi Pengeluaran Keluarga", color_discrete_sequence=px.colors.sequential.Rainbow)
            fig.update_layout(font=dict(size=18))
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("MINAT PELATIHAN")
        df_training = get_data(f"""
            SELECT 
                Pelatihan,
                COUNT(*) AS jumlah
            FROM
            (
                SELECT `Pelatihan_Diminati_I` AS Pelatihan
                FROM data_demografi
                WHERE `Pelatihan_Diminati_I` IS NOT NULL
                {month_condition}

                UNION ALL

                SELECT `Pelatihan_Diminati_II`
                FROM data_demografi
                WHERE `Pelatihan_Diminati_II` IS NOT NULL
                {month_condition}

                UNION ALL

                SELECT `Pelatihan_Diminati_III`
                FROM data_demografi
                WHERE `Pelatihan_Diminati_III` IS NOT NULL
                {month_condition}
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
            )
            GROUP BY Pelatihan
            ORDER BY jumlah DESC
        """)

        if not df_training.empty:
            # Hitung total peserta pelatihan
            total_peserta = df_training['jumlah'].sum()
            
            # Tambahkan kolom persentase
            df_training['persentase'] = (df_training['jumlah'] / total_peserta) * 100

            # Buat pie chart dengan persentase
            fig = px.pie(df_training, names='Pelatihan', values='persentase', title="Minat Pelatihan (Persentase)",
                        color_discrete_sequence=px.colors.sequential.Sunsetdark, hole=0.3)
            fig.update_layout(font=dict(size=18))

            # Tambahkan label persentase pada chart
            fig.update_traces(textinfo='percent+label')

            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("KK MILENIAL")
        df_kk_millennial = get_data(f"""
            SELECT 
                `Milenial_Non_Milenial` AS Kategori,
                COUNT(DISTINCT `No_KK`) AS jumlah_KK
            FROM data_demografi
            WHERE `Milenial_Non_Milenial` IS NOT NULL  
            {month_condition}
            GROUP BY `Milenial_Non_Milenial`
            ORDER BY jumlah_KK DESC
        """)

        if not df_kk_millennial.empty:
            fig = px.pie(df_kk_millennial, names='Kategori', values='jumlah_KK',
                        title="Distribusi KK Milenial", color_discrete_sequence=px.colors.sequential.Burg)
            fig.update_layout(font=dict(size=18))
            st.plotly_chart(fig, use_container_width=True)


elif selected_page == "Tunggakan dan Kepemilikan":

    with col1:

        

        

        
        
        # # --- Visualisasi Jumlah Orang yang Menunggak per UPRS ---
        # st.subheader("UPRS dengan Jumlah Orang yang Menunggak Terbanyak")
        # df_tunggakan_uprs = get_data(f"""
        #     SELECT d.UPRS AS Nama_UPRS, COUNT(DISTINCT t.ktp) AS Jumlah_Penunggak
        #     FROM tb_tunggakan t
        #     JOIN data_demografi d ON t.ktp COLLATE utf8mb4_unicode_ci = d.NIK COLLATE utf8mb4_unicode_ci
        #     WHERE t.ktp COLLATE utf8mb4_unicode_ci IN (SELECT DISTINCT NIK COLLATE utf8mb4_unicode_ci FROM data_demografi)
        #     {month_condition}
        #     GROUP BY d.UPRS
        #     HAVING Jumlah_Penunggak > 0
        #     ORDER BY Jumlah_Penunggak DESC
        # """)

        # if not df_tunggakan_uprs.empty:
        #     fig = px.bar(df_tunggakan_uprs, x='Jumlah_Penunggak', y='Nama_UPRS', orientation='h',
        #                 title="UPRS dengan Jumlah Orang yang Menunggak Terbanyak",
        #                 color='Jumlah_Penunggak', color_continuous_scale=px.colors.sequential.Sunset)

        #     st.plotly_chart(fig, use_container_width=True)
        # else:
        #     st.warning("Tidak ada data tunggakan yang tersedia untuk bulan yang dipilih.")


        
        
        st.subheader("TREN JUMLAH ORANG YANG MENUNGGAK PER TAHUN")

        df_tunggakan_tahun = get_data("""
            SELECT t.bill_year AS Tahun, COUNT(DISTINCT t.ktp) AS Jumlah_Penunggak
            FROM tb_tunggakan t
            WHERE t.bill_year IS NOT NULL AND t.bill_year > 0  -- Hanya ambil tahun lebih besar dari 0
            GROUP BY t.bill_year
            ORDER BY t.bill_year ASC
        """)

        if not df_tunggakan_tahun.empty:
            # Pastikan Tahun berupa integer untuk menghindari nilai tidak valid
            df_tunggakan_tahun["Tahun"] = pd.to_numeric(df_tunggakan_tahun["Tahun"], errors="coerce")
            
            # Hapus data dengan tahun yang tidak valid (misalnya NULL atau non-numeric)
            df_tunggakan_tahun = df_tunggakan_tahun.dropna()
            
            # Konversi ke integer setelah menghapus nilai tidak valid
            df_tunggakan_tahun["Tahun"] = df_tunggakan_tahun["Tahun"].astype(int)

            # Buat visualisasi line chart
            fig = px.line(df_tunggakan_tahun, x='Tahun', y='Jumlah_Penunggak', markers=True,
                        title="Grafik Tren Jumlah Orang yang Menunggak per Tahun",
                        labels={"Tahun": "Tahun", "Jumlah_Penunggak": "Jumlah Orang Menunggak"},
                        line_shape="linear", text='Jumlah_Penunggak')

            fig.update_traces(line=dict(width=2), marker=dict(size=6), textposition='top center')
            fig.update_layout(font=dict(size=18),
                            margin=dict(l=50, r=50, t=100, b=50),
                            yaxis=dict(title="Jumlah Orang Menunggak", automargin=True))

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada data tunggakan yang tersedia untuk ditampilkan.")

        
        # --- Visualisasi Jumlah Jiwa Berdasarkan Wilayah dan UPRS ---
        st.subheader("JUMLAH JIWA PER WILAYAH dan UPRS")

        df_wilayah_uprs = get_data("""
            SELECT d.Wilayah, d.UPRS, COUNT(*) AS Total_Jiwa
            FROM data_demografi d
            WHERE d.Wilayah IS NOT NULL AND d.UPRS IS NOT NULL
            GROUP BY d.Wilayah, d.UPRS
            ORDER BY d.Wilayah, d.UPRS
        """)

        if not df_wilayah_uprs.empty:
            # Buat stacked bar chart
            fig = px.bar(df_wilayah_uprs, x="Wilayah", y="Total_Jiwa", color="UPRS",
                        title="Jumlah Jiwa Berdasarkan Wilayah dan UPRS",
                        labels={"Total_Jiwa": "Jumlah Jiwa", "Wilayah": "Wilayah"},
                        barmode="stack", text_auto=True)  # Tambahkan angka pada batang
            fig.update_layout(font=dict(size=12))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada data jiwa yang tersedia untuk ditampilkan.")


        # --- Visualisasi Tren Jumlah Orang yang Menunggak per Tahun ---
        st.subheader("KEPEMILIKAN DENGAN TUNGGAKAN")
        # Query untuk mendapatkan data kepemilikan dan status tunggakan
        # Query untuk mendapatkan data kepemilikan dan status tunggakan dengan collation yang disamakan
        df_tunggakan_kepemilikan = get_data(f"""
            SELECT 
                CASE 
                    WHEN t.ktp IS NOT NULL THEN 'Memiliki Tunggakan'
                    ELSE 'Tidak Memiliki Tunggakan'
                END AS Status_Tunggakan,
                COUNT(DISTINCT k.nik) AS jumlah
            FROM tb_kepemilikan k
            LEFT JOIN tb_tunggakan t ON CONVERT(k.nik USING utf8mb4) = CONVERT(t.ktp USING utf8mb4)
            GROUP BY Status_Tunggakan
        """)

        # Jika data tersedia, buat pie chart
        if not df_tunggakan_kepemilikan.empty:
            total_orang = df_tunggakan_kepemilikan["jumlah"].sum()
            df_tunggakan_kepemilikan["persentase"] = (df_tunggakan_kepemilikan["jumlah"] / total_orang) * 100

            fig = px.pie(df_tunggakan_kepemilikan, names="Status_Tunggakan", values="persentase", 
                        title="Persentase Kepemilikan Aset Berdasarkan Status Tunggakan",
                        color_discrete_sequence=px.colors.sequential.Plasma, hole=0.3)
            fig.update_layout(font=dict(size=12))
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada data kepemilikan atau tunggakan yang tersedia.")
        

    with col2:
        
        
        st.subheader("DISTRIBUSI ALASAN TUNGGAKAN")
        df_failed_reason = get_data(f"""
            SELECT failed_reason, COUNT(*) AS jumlah
            FROM tb_tunggakan
            WHERE failed_reason IS NOT NULL AND failed_reason != ''
            {month_condition}
            GROUP BY failed_reason
            ORDER BY jumlah DESC
        """)

        if not df_failed_reason.empty:
            fig = px.pie(df_failed_reason, names='failed_reason', values='jumlah', 
                        title="Distribusi Alasan Tunggakan", 
                        color_discrete_sequence=px.colors.sequential.Magma, 
                        hole=0.3)  # Menyesuaikan ukuran agar lebih mirip dengan diagram pendidikan
            
            fig.update_layout(font=dict(size=14), height=500, width=500)  # Sesuaikan ukuran agar proporsional
            fig.update_traces(textinfo='percent+label')  # Tambahkan label persentase
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada data alasan tunggakan yang tersedia.")

        st.subheader("JUMLAH KENDARAAN RODA 2 dan RODA 4 Per UPRS")

        df_kendaraan = get_data("""
            SELECT d.UPRS AS Nama_UPRS, 
                SUM(COALESCE(k.roda_dua, 0)) AS Total_Roda_Dua, 
                SUM(COALESCE(k.roda_empat, 0)) AS Total_Roda_Empat
            FROM tb_kepemilikan k
            JOIN data_demografi d ON k.nik = d.NIK
            WHERE k.nik IN (SELECT DISTINCT NIK FROM data_demografi)  
            GROUP BY d.UPRS
        """)

        if not df_kendaraan.empty:
            # Pastikan Nama_UPRS memiliki urutan yang benar
            uprs_order = ["UPRS I", "UPRS II", "UPRS III", "UPRS IV", "UPRS V", "UPRS VI", "UPRS VII", "UPRS VIII"]
            
            # Konversi kategori ke dalam urutan yang benar
            df_kendaraan["Nama_UPRS"] = pd.Categorical(df_kendaraan["Nama_UPRS"], categories=uprs_order, ordered=True)
            
            # Urutkan berdasarkan kategori yang sudah diatur
            df_kendaraan = df_kendaraan.sort_values("Nama_UPRS")

            # Ubah nama kolom agar lebih rapi dalam visualisasi
            df_kendaraan = df_kendaraan.rename(columns={
                "Total_Roda_Dua": "Total Roda Dua",
                "Total_Roda_Empat": "Total Roda Empat"
            })

            # Transformasi data untuk visualisasi
            df_melted = df_kendaraan.melt(id_vars="Nama_UPRS", 
                                        value_vars=["Total Roda Dua", "Total Roda Empat"], 
                                        var_name="Jenis Kendaraan", 
                                        value_name="Jumlah")

            # Buat bar chart dengan angka di atas bar
            fig = px.bar(df_melted, x="Nama_UPRS", y="Jumlah", color="Jenis Kendaraan", 
                        title="Jumlah Kendaraan Roda 2 dan Roda 4 per UPRS",
                        barmode="group",
                        labels={"Jumlah": "Total Kendaraan", "Nama_UPRS": "UPRS"},
                        color_discrete_map={"Total Roda Dua": "blue", "Total Roda Empat": "red"},
                        text_auto=True)  # Tambahkan angka pada batang
            
            fig.update_layout(font=dict(size=20),
                            margin=dict(l=50, r=50, t=80, b=50),
                            yaxis=dict(title="Total Kendaraan", automargin=True))
            
            fig.update_traces(textfont_size=16, textposition='outside')
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada data kendaraan yang tersedia.")
        
        st.subheader("KEPEMILIKAN ASET BERDASARKAN STATUS TUNGGAKAN")

        # Query untuk mendapatkan data kepemilikan berdasarkan tunggakan dengan kategori lebih rinci
        df_kepemilikan_tunggakan = get_data(f"""
            SELECT 
                CASE 
                    WHEN k.roda_empat > 0 AND k.roda_dua > 0 AND k.pbb > 0 THEN 'Memiliki Roda Empat, Roda Dua, dan PBB'
                    WHEN k.roda_empat > 0 AND k.roda_dua > 0 THEN 'Memiliki Roda Empat dan Roda Dua'
                    WHEN k.roda_empat > 0 AND k.pbb > 0 THEN 'Memiliki Roda Empat dan PBB'
                    WHEN k.roda_dua > 0 AND k.pbb > 0 THEN 'Memiliki Roda Dua dan PBB'
                    WHEN k.roda_empat > 0 THEN 'Memiliki Roda Empat'
                    WHEN k.roda_dua > 0 THEN 'Memiliki Roda Dua'
                    WHEN k.pbb > 0 THEN 'Memiliki PBB'
                    ELSE 'Tidak Punya'
                END AS Kategori_Kepemilikan,
                COUNT(DISTINCT k.nik) AS jumlah
            FROM tb_kepemilikan k
            JOIN tb_tunggakan t ON CONVERT(k.nik USING utf8mb4) = CONVERT(t.ktp USING utf8mb4)
            GROUP BY Kategori_Kepemilikan
        """)

        # Jika data tersedia, buat pie chart
        if not df_kepemilikan_tunggakan.empty:
            total_orang = df_kepemilikan_tunggakan["jumlah"].sum()
            df_kepemilikan_tunggakan["persentase"] = (df_kepemilikan_tunggakan["jumlah"] / total_orang) * 100

            fig = px.pie(df_kepemilikan_tunggakan, names="Kategori_Kepemilikan", values="persentase", 
                        title="Persentase Kepemilikan Aset bagi yang Memiliki Tunggakan",
                        color_discrete_sequence=px.colors.sequential.Rainbow, hole=0.3)
            fig.update_layout(font=dict(size=12))
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Tidak ada data kepemilikan atau tunggakan yang tersedia.")