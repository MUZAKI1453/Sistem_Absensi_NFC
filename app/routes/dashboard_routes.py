from flask import Blueprint, render_template, session, redirect
from datetime import date
from app.models.database import get_db   # ← INI YANG PENTING DITAMBAHKAN

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
def dashboard_page():

    if "login" not in session:
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    today = date.today().isoformat()   # '2026-04-02'

    # Total Kelas & Siswa (keseluruhan)
    total_kelas = c.execute("SELECT COUNT(*) FROM kelas").fetchone()[0]
    total_siswa = c.execute("SELECT COUNT(*) FROM siswa").fetchone()[0]

    # ================= REKAP ABSENSI HARI INI SAJA =================
    query_rekap = """
        SELECT 
            COUNT(CASE WHEN status = 'hadir' THEN 1 END) as hadir,
            COUNT(CASE WHEN status = 'sakit' THEN 1 END) as sakit,
            COUNT(CASE WHEN status = 'izin'  THEN 1 END) as izin,
            COUNT(CASE WHEN status = 'alfa'  THEN 1 END) as alfa
        FROM absensi 
        WHERE DATE(waktu) = ?
    """

    rekap = c.execute(query_rekap, (today,)).fetchone()

    hadir = rekap["hadir"] if rekap else 0
    sakit = rekap["sakit"] if rekap else 0
    izin  = rekap["izin"]  if rekap else 0
    alfa  = rekap["alfa"]  if rekap else 0

    # 10 Absensi Terbaru Hari Ini
    data = c.execute("""
        SELECT siswa.nama, absensi.status, absensi.waktu
        FROM absensi
        JOIN siswa ON siswa.id = absensi.siswa_id
        WHERE DATE(absensi.waktu) = ?
        ORDER BY absensi.waktu DESC
        LIMIT 10
    """, (today,)).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_kelas=total_kelas,
        total_siswa=total_siswa,
        hadir=hadir,
        sakit=sakit,
        izin=izin,
        alfa=alfa,
        data=data,
        today=today
    )