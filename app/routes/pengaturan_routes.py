from flask import Blueprint, render_template, request, redirect, session, flash
from app.models.database import get_db

pengaturan = Blueprint("pengaturan", __name__)

# =========================
# HALAMAN PENGATURAN
# =========================
@pengaturan.route("/pengaturan", methods=["GET", "POST"])
def halaman_pengaturan():

    if "login" not in session:
        return redirect("/")

    conn = get_db()

    # =========================
    # SIMPAN DATA
    # =========================
    if request.method == "POST":

        jam_masuk   = request.form.get("jam_masuk")
        batas_telat = request.form.get("batas_telat")
        jam_pulang  = request.form.get("jam_pulang")

        if not jam_masuk or not batas_telat or not jam_pulang:
            flash("Semua field wajib diisi", "warning")
            return redirect("/pengaturan")

        cek = conn.execute("SELECT * FROM pengaturan").fetchone()

        if cek:
            conn.execute("""
                UPDATE pengaturan
                SET jam_masuk=?, batas_telat=?, jam_pulang=?
                WHERE id=1
            """, (jam_masuk, batas_telat, jam_pulang))
        else:
            conn.execute("""
                INSERT INTO pengaturan(jam_masuk, batas_telat, jam_pulang)
                VALUES(?,?,?)
            """, (jam_masuk, batas_telat, jam_pulang))

        conn.commit()
        conn.close()

        flash("Pengaturan berhasil disimpan", "success")
        return redirect("/pengaturan")

    # =========================
    # AMBIL DATA
    # =========================
    data = conn.execute("SELECT * FROM pengaturan").fetchone()
    conn.close()

    return render_template("pengaturan.html", data=data)