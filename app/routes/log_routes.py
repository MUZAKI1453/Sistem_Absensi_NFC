from datetime import datetime

from flask import Blueprint, render_template, request, redirect, session, flash
from app.models.database import get_db

log = Blueprint("log", __name__)


# =========================
# HALAMAN LOG ABSENSI
# =========================
@log.route("/log")
def halaman_log():

    if "login" not in session:
        return redirect("/")

    # ================= FILTER =================
    tanggal = request.args.get("tanggal")
    bulan   = request.args.get("bulan")
    tahun   = request.args.get("tahun")
    status  = request.args.get("status")

    # Jika tidak ada filter tanggal sama sekali, default ke HARI INI
    if not tanggal and not (bulan and tahun):
        from datetime import date
        today = date.today()
        tanggal = today.strftime("%Y-%m-%d")   # contoh: 2026-04-02

    query = """
        SELECT 
            absensi.id,
            siswa.nama,
            siswa.nis,
            kelas.nama_kelas,
            absensi.status,
            absensi.waktu
        FROM absensi
        JOIN siswa ON absensi.siswa_id = siswa.id
        LEFT JOIN kelas ON siswa.kelas_id = kelas.id
    """

    kondisi = []
    params = []

    # Filter tanggal spesifik
    if tanggal:
        kondisi.append("DATE(absensi.waktu) = ?")
        params.append(tanggal)

    # Filter bulan + tahun
    elif bulan and tahun:          # hanya dipakai kalau tidak pakai tanggal
        kondisi.append("strftime('%m', absensi.waktu) = ?")
        kondisi.append("strftime('%Y', absensi.waktu) = ?")
        params.append(bulan.zfill(2))
        params.append(tahun)

    # Filter status
    if status:
        kondisi.append("absensi.status = ?")
        params.append(status)

    if kondisi:
        query += " WHERE " + " AND ".join(kondisi)

    query += " ORDER BY absensi.waktu DESC"

    with get_db() as conn:
        data = conn.execute(query, params).fetchall()

    return render_template(
        "log.html",
        log=data,
        tanggal=tanggal,
        bulan=bulan,
        tahun=tahun,
        status=status,
        today=datetime.now().strftime("%Y-%m-%d")   # kirim today ke template
    )


# =========================
# UPDATE STATUS ABSENSI
# =========================
@log.route("/update_absen/<int:id>", methods=["POST"])
def update_absen(id):

    if "login" not in session:
        return redirect("/")

    status = request.form.get("status")

    if status not in ["hadir", "sakit", "izin", "alfa"]:
        flash("Status tidak valid", "warning")
        return redirect("/log")

    with get_db() as conn:
        conn.execute("""
            UPDATE absensi
            SET status=?
            WHERE id=?
        """, (status, id))
        conn.commit()

    flash("Status absensi diperbarui", "success")
    return redirect("/log")