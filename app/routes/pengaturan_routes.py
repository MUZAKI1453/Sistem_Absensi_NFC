from flask import Blueprint, render_template, request, redirect, session, flash
from datetime import datetime
from app.models.database import get_db

pengaturan = Blueprint("pengaturan", __name__)


# =========================
# HALAMAN PENGATURAN
# =========================
@pengaturan.route("/pengaturan", methods=["GET", "POST"])
def halaman_pengaturan():

    if "login" not in session:
        return redirect("/")

    with get_db() as conn:
        c = conn.cursor()

        if request.method == "POST":
            jam_masuk       = request.form.get("jam_masuk", "").strip()
            jam_masuk_akhir = request.form.get("jam_masuk_akhir", "").strip()
            batas_telat     = request.form.get("batas_telat", "").strip()
            jam_pulang      = request.form.get("jam_pulang", "").strip()

            # Validasi: semua field wajib diisi
            if not jam_masuk or not jam_masuk_akhir or not batas_telat or not jam_pulang:
                flash("Semua field jam harus diisi!", "warning")
                return redirect("/pengaturan")

            # Validasi format jam (HH:MM)
            try:
                datetime.strptime(jam_masuk, "%H:%M")
                datetime.strptime(jam_masuk_akhir, "%H:%M")
                datetime.strptime(batas_telat, "%H:%M")
                datetime.strptime(jam_pulang, "%H:%M")
            except ValueError:
                flash("Format jam harus HH:MM (contoh: 07:30)", "danger")
                return redirect("/pengaturan")

            # Validasi logika waktu: jam_masuk_akhir harus setelah jam_masuk
            if jam_masuk_akhir <= jam_masuk:
                flash("Jam Masuk Akhir harus lebih besar dari Jam Masuk", "danger")
                return redirect("/pengaturan")

            if batas_telat <= jam_masuk_akhir:
                flash("Batas Telat harus lebih besar dari Jam Masuk Akhir", "danger")
                return redirect("/pengaturan")

            # Cek apakah data pengaturan sudah ada
            existing = c.execute("SELECT id FROM pengaturan LIMIT 1").fetchone()

            if existing:
                # Update
                c.execute("""
                    UPDATE pengaturan
                    SET jam_masuk = ?,
                        jam_masuk_akhir = ?,
                        batas_telat = ?,
                        jam_pulang = ?
                    WHERE id = 1
                """, (jam_masuk, jam_masuk_akhir, batas_telat, jam_pulang))
            else:
                # Insert baru
                c.execute("""
                    INSERT INTO pengaturan (jam_masuk, jam_masuk_akhir, batas_telat, jam_pulang)
                    VALUES (?, ?, ?, ?)
                """, (jam_masuk, jam_masuk_akhir, batas_telat, jam_pulang))

            conn.commit()
            flash("Pengaturan berhasil disimpan ✓", "success")
            return redirect("/pengaturan")

        # ==================== AMBIL DATA ====================
        data = c.execute("SELECT * FROM pengaturan LIMIT 1").fetchone()

    # Jika belum ada data pengaturan
    if data is None:
        data = {
            "jam_masuk": "",
            "jam_masuk_akhir": "",
            "batas_telat": "",
            "jam_pulang": ""
        }

    return render_template("pengaturan.html", data=data)