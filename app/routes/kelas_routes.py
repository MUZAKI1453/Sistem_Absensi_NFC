from flask import Blueprint, render_template, request, redirect, session, flash
from app.models.database import get_db

kelas = Blueprint("kelas", __name__)


# =========================
# READ DATA KELAS
# =========================
@kelas.route("/kelas")
def halaman_kelas():

    if "login" not in session:
        return redirect("/")

    conn = get_db()

    data = conn.execute("""
        SELECT k.id, k.nama_kelas, COUNT(s.id) as jumlah_siswa
        FROM kelas k
        LEFT JOIN siswa s ON s.kelas_id = k.id
        GROUP BY k.id
        ORDER BY k.id DESC
    """).fetchall()

    conn.close()

    return render_template("kelas.html", kelas=data)


# =========================
# TAMBAH KELAS
# =========================
@kelas.route("/tambah_kelas", methods=["POST"])
def tambah_kelas():

    if "login" not in session:
        return redirect("/")

    nama = request.form.get("nama_kelas")

    if not nama:
        flash("Nama kelas tidak boleh kosong", "warning")
        return redirect("/kelas")

    conn = get_db()

    # cek duplikat
    if conn.execute("SELECT 1 FROM kelas WHERE nama_kelas=?", (nama,)).fetchone():
        conn.close()
        flash("Kelas sudah ada", "warning")
        return redirect("/kelas")

    conn.execute(
        "INSERT INTO kelas(nama_kelas) VALUES(?)",
        (nama,)
    )

    conn.commit()
    conn.close()

    flash("Kelas berhasil ditambahkan", "success")

    return redirect("/kelas")


# =========================
# DELETE KELAS
# =========================
@kelas.route("/delete_kelas/<int:id>")
def delete_kelas(id):

    if "login" not in session:
        return redirect("/")

    conn = get_db()

    try:
        # CEK APAKAH MASIH ADA SISWA
        siswa = conn.execute("""
            SELECT COUNT(*) as total 
            FROM siswa 
            WHERE kelas_id = ?
        """, (id,)).fetchone()

        if siswa["total"] > 0:
            conn.close()
            flash("Kelas tidak bisa dihapus karena masih ada data siswa!", "warning")
            return redirect("/kelas")

        # AMAN DIHAPUS
        conn.execute("DELETE FROM kelas WHERE id=?", (id,))
        conn.commit()
        conn.close()

        flash("Kelas berhasil dihapus", "danger")

    except Exception as e:
        print("ERROR DELETE KELAS:", e)
        flash("Terjadi kesalahan saat menghapus kelas", "danger")

    return redirect("/kelas")


# =========================
# EDIT KELAS
# =========================
@kelas.route("/edit_kelas/<int:id>", methods=["POST"])
def edit_kelas(id):

    if "login" not in session:
        return redirect("/")

    nama = request.form.get("nama_kelas")

    if not nama:
        flash("Nama kelas tidak boleh kosong", "warning")
        return redirect("/kelas")

    conn = get_db()

    # cek duplikat
    cek = conn.execute("""
        SELECT 1 FROM kelas WHERE nama_kelas=? AND id!=?
    """, (nama, id)).fetchone()

    if cek:
        conn.close()
        flash("Nama kelas sudah digunakan", "warning")
        return redirect("/kelas")

    conn.execute("""
        UPDATE kelas SET nama_kelas=? WHERE id=?
    """, (nama, id))

    conn.commit()
    conn.close()

    flash("Kelas berhasil diperbarui", "success")

    return redirect("/kelas")