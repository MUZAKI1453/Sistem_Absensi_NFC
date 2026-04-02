from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.database import get_db
import app

scan = Blueprint("scan", __name__)

last_uid = None


# ==========================
# SCAN KARTU DARI ESP8266
# ==========================
@scan.route("/scan")
def scan_nfc():

    global last_uid

    uid = request.args.get("uid")

    print("Kartu diterima:", uid)

    # ==========================
    # MODE REGISTER
    # ==========================
    if app.mode == "register":
        last_uid = uid
        return "REGISTER MODE"

    # ==========================
    # MODE ABSENSI
    # ==========================
    conn = get_db()
    c = conn.cursor()

    siswa = c.execute(
        "SELECT id, nama FROM siswa WHERE uid=?",
        (uid,)
    ).fetchone()

    if not siswa:
        conn.close()
        return "KARTU TIDAK TERDAFTAR !"

    siswa_id = siswa["id"]
    nama = siswa["nama"]

    now = datetime.now()

    # ==========================
    # AMBIL PENGATURAN (WAJIB)
    # ==========================
    pengaturan = c.execute(
        "SELECT * FROM pengaturan LIMIT 1"
    ).fetchone()

    if not pengaturan:
        conn.close()
        return "PENGATURAN BELUM DISET"

    jam_masuk = datetime.strptime(
        pengaturan["jam_masuk"], "%H:%M"
    ).time()

    batas_telat = datetime.strptime(
        pengaturan["batas_telat"], "%H:%M"
    ).time()

    # ==========================
    # CEK SUDAH ABSEN HARI INI
    # ==========================
    cek = c.execute(
        """
        SELECT * FROM absensi 
        WHERE siswa_id=? AND DATE(waktu)=DATE('now')
        """,
        (siswa_id,)
    ).fetchone()

    if cek:
        conn.close()
        return f"{nama} SUDAH ABSEN !"

    # ==========================
    # LOGIKA STATUS (FIX TOTAL)
    # ==========================
    if now.time() <= jam_masuk:
        status = "hadir"
        menit_telat = 0

    elif now.time() <= batas_telat:
        status = "telat"

        selisih = datetime.combine(now.date(), now.time()) - \
                  datetime.combine(now.date(), jam_masuk)

        menit_telat = int(selisih.total_seconds() / 60)

    else:
        status = "alfa"
        menit_telat = 0

    # ==========================
    # SIMPAN ABSENSI
    # ==========================
    c.execute(
        """
        INSERT INTO absensi(siswa_id, status, menit_telat)
        VALUES(?,?,?)
        """,
        (siswa_id, status, menit_telat)
    )

    conn.commit()
    conn.close()

    return f"{nama} - {status.upper()}"


# ==========================
# AMBIL UID TERAKHIR
# ==========================
@scan.route("/get_uid")
def get_uid():
    global last_uid

    return jsonify({
        "uid": last_uid
    })


# ==========================
# RESET UID (PENTING)
# ==========================
@scan.route("/reset_uid")
def reset_uid():

    global last_uid
    last_uid = None

    return jsonify({
        "status": "reset"
    })


# ==========================
# MODE PERANGKAT
# ==========================
@scan.route("/mode")
def get_mode():
    return app.mode