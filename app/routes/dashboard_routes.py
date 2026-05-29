from flask import Blueprint, render_template, session, redirect, jsonify
from datetime import date
from app.models.database import get_db

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
def dashboard_page():
    if "login" not in session:
        return redirect("/")

    today = date.today().isoformat()

    with get_db() as conn:
        c = conn.cursor()

        total_kelas = c.execute("SELECT COUNT(*) FROM kelas").fetchone()[0] or 0
        total_siswa = c.execute("SELECT COUNT(*) FROM siswa").fetchone()[0] or 0

        rekap = c.execute("""
            SELECT 
                COUNT(CASE WHEN COALESCE(absensi.status, 'alfa') = 'hadir' THEN 1 END) as hadir,
                COUNT(CASE WHEN COALESCE(absensi.status, 'alfa') = 'sakit' THEN 1 END) as sakit,
                COUNT(CASE WHEN COALESCE(absensi.status, 'alfa') = 'izin'  THEN 1 END) as izin,
                COUNT(CASE WHEN COALESCE(absensi.status, 'alfa') = 'alfa'  THEN 1 END) as alfa,
                SUM(CASE WHEN absensi.menit_telat > 0 THEN 1 ELSE 0 END) as total_telat
            FROM siswa
            LEFT JOIN absensi ON siswa.id = absensi.siswa_id 
                             AND absensi.tanggal = ?
        """, (today,)).fetchone()

    return render_template(
        "dashboard.html",
        total_kelas=total_kelas,
        total_siswa=total_siswa,
        hadir=rekap["hadir"] or 0,
        sakit=rekap["sakit"] or 0,
        izin=rekap["izin"] or 0,
        alfa=rekap["alfa"] or 0,
        total_telat=rekap["total_telat"] or 0
    )


# =========================
# 🔥 ENDPOINT AJAX (RINGAN)
# =========================
@dashboard.route("/dashboard/data")
def dashboard_data():
    today = date.today().isoformat()

    with get_db() as conn:
        c = conn.cursor()

        total_kelas = c.execute("SELECT COUNT(*) FROM kelas").fetchone()[0] or 0
        total_siswa = c.execute("SELECT COUNT(*) FROM siswa").fetchone()[0] or 0

        rekap = c.execute("""
            SELECT 
                COUNT(CASE WHEN COALESCE(absensi.status, 'alfa') = 'hadir' THEN 1 END) as hadir,
                COUNT(CASE WHEN COALESCE(absensi.status, 'alfa') = 'sakit' THEN 1 END) as sakit,
                COUNT(CASE WHEN COALESCE(absensi.status, 'alfa') = 'izin'  THEN 1 END) as izin,
                COUNT(CASE WHEN COALESCE(absensi.status, 'alfa') = 'alfa'  THEN 1 END) as alfa,
                SUM(CASE WHEN absensi.menit_telat > 0 THEN 1 ELSE 0 END) as total_telat
            FROM siswa
            LEFT JOIN absensi ON siswa.id = absensi.siswa_id 
                             AND absensi.tanggal = ?
        """, (today,)).fetchone()

    return jsonify({
        "kelas": total_kelas,
        "siswa": total_siswa,
        "hadir": rekap["hadir"] or 0,
        "sakit": rekap["sakit"] or 0,
        "izin": rekap["izin"] or 0,
        "alfa": rekap["alfa"] or 0,
        "telat": rekap["total_telat"] or 0
    })