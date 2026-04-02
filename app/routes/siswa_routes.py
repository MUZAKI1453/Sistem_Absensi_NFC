from flask import Blueprint, render_template, request, redirect, session, flash
from app.models.database import get_db
import app

siswa = Blueprint("siswa", __name__)


# =========================
# READ DATA SISWA
# =========================
@siswa.route("/siswa")
def halaman_siswa():

    if "login" not in session:
        return redirect("/")

    app.mode = "absen"

    with get_db() as conn:
        data = conn.execute("""
            SELECT siswa.id, siswa.nama, siswa.nis, siswa.uid, kelas.nama_kelas
            FROM siswa
            LEFT JOIN kelas ON siswa.kelas_id = kelas.id
            ORDER BY siswa.id DESC
        """).fetchall()

        kelas_list = conn.execute("SELECT * FROM kelas").fetchall()

    return render_template(
        "siswa.html",
        siswa=data,
        kelas_list=kelas_list
    )


# =========================
# REGISTER KARTU (FIX FINAL)
# =========================
@siswa.route("/register", methods=["GET", "POST"])
def register_kartu():

    if "login" not in session:
        return redirect("/")

    # ================= POST =================
    if request.method == "POST":

        nama = request.form.get("nama")
        nis  = request.form.get("nis")
        uid  = request.form.get("uid")
        kelas_id = request.form.get("kelas_id")

        # VALIDASI
        if not nama or not nis or not uid or not kelas_id:
            flash("Semua field wajib diisi", "warning")
            return redirect("/register")

        try:
            kelas_id = int(kelas_id)
        except:
            flash("Kelas tidak valid", "danger")
            return redirect("/register")

        try:
            with get_db() as conn:

                # CEK NIS
                if conn.execute("SELECT 1 FROM siswa WHERE nis=?", (nis,)).fetchone():
                    flash("NIS sudah digunakan", "warning")
                    return redirect("/register")

                # CEK UID
                if conn.execute("SELECT 1 FROM siswa WHERE uid=?", (uid,)).fetchone():
                    flash("Kartu sudah terdaftar", "danger")
                    return redirect("/register")

                # SIMPAN
                conn.execute("""
                    INSERT INTO siswa(nama, nis, uid, kelas_id)
                    VALUES(?,?,?,?)
                """, (nama, nis, uid, kelas_id))

                conn.commit()

            app.mode = "absen"
            flash("Registrasi siswa berhasil", "success")

            return redirect("/siswa")

        except Exception as e:
            print("ERROR REGISTER:", e)
            flash("Terjadi kesalahan saat menyimpan data", "danger")
            return redirect("/register")

    # ================= GET =================
    with get_db() as conn:
        kelas = conn.execute("SELECT * FROM kelas").fetchall()

    app.mode = "register"

    return render_template("register.html", kelas=kelas)


# =========================
# DELETE SISWA (ANTI LOCK)
# =========================
@siswa.route("/delete_siswa/<int:id>")
def delete_siswa(id):

    if "login" not in session:
        return redirect("/")

    try:
        with get_db() as conn:
            conn.execute("DELETE FROM siswa WHERE id=?", (id,))
            conn.commit()

        flash("Data siswa berhasil dihapus", "danger")

    except Exception as e:
        print("ERROR DELETE:", e)
        flash("Gagal menghapus (database sibuk / terkunci)", "danger")

    return redirect("/siswa")


# =========================
# EDIT SISWA (FIX)
# =========================
@siswa.route("/edit_siswa/<int:id>", methods=["POST"])
def edit_siswa(id):

    if "login" not in session:
        return redirect("/")

    nama = request.form.get("nama")
    nis  = request.form.get("nis")
    kelas_id = request.form.get("kelas_id")

    if not nama or not nis or not kelas_id:
        flash("Data tidak boleh kosong", "warning")
        return redirect("/siswa")

    try:
        kelas_id = int(kelas_id)
    except:
        flash("Kelas tidak valid", "danger")
        return redirect("/siswa")

    try:
        with get_db() as conn:

            # cek NIS unik
            cek = conn.execute("""
                SELECT 1 FROM siswa WHERE nis=? AND id!=?
            """, (nis, id)).fetchone()

            if cek:
                flash("NIS sudah digunakan", "warning")
                return redirect("/siswa")

            conn.execute("""
                UPDATE siswa 
                SET nama=?, nis=?, kelas_id=? 
                WHERE id=?
            """, (nama, nis, kelas_id, id))

            conn.commit()

        flash("Data siswa berhasil diperbarui", "success")

    except Exception as e:
        print("ERROR EDIT:", e)
        flash("Gagal mengupdate data", "danger")

    return redirect("/siswa")