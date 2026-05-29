from flask import Blueprint, render_template, redirect, session
from app.models.database import get_db

device = Blueprint("device", __name__)


# ================= LIST DEVICE =================
@device.route("/device")
def halaman_device():

    if "login" not in session:
        return redirect("/")

    with get_db() as conn:
        data = conn.execute("SELECT * FROM device ORDER BY id DESC").fetchall()

    return render_template("device.html", device=data)


# ================= AKTIFKAN =================
@device.route("/device_on/<int:id>")
def aktifkan(id):

    with get_db() as conn:
        conn.execute("UPDATE device SET is_active=1 WHERE id=?", (id,))
        conn.commit()

    return redirect("/device")


# ================= NONAKTIF =================
@device.route("/device_off/<int:id>")
def nonaktifkan(id):

    with get_db() as conn:
        conn.execute("UPDATE device SET is_active=0 WHERE id=?", (id,))
        conn.commit()

    return redirect("/device")