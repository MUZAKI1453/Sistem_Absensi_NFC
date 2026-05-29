from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.database import get_db
import app

scan = Blueprint("scan", __name__)

last_uid = None
SECRET_KEY_DEVICE = "RAHASIA_SUPER_123"


@scan.route("/scan")
def scan_nfc():

    mac = request.args.get("mac")
    key = request.args.get("key")

    # ================= VALIDASI DASAR =================
    if not mac or not key:
        return "REQUEST TIDAK VALID"

    # ================= VALIDASI KEY =================
    if key != SECRET_KEY_DEVICE:
        return "AKSES DITOLAK"

    with get_db() as conn:
        c = conn.cursor()

        device = c.execute("SELECT * FROM device WHERE mac=?", (mac,)).fetchone()

        # ================= AUTO REGISTER =================
        if not device:
            c.execute("""
                      INSERT INTO device(mac, last_seen, is_active)
                      VALUES (?, ?, 0)
                      """, (mac, datetime.now()))
            conn.commit()
            return "DEVICE BARU - HUBUNGI ADMIN"

        # ================= CEK STATUS =================
        if device["is_active"] == 0:
            return "DEVICE BELUM DIAKTIFKAN"

        # ================= UPDATE LAST SEEN =================
        c.execute("""
                  UPDATE device
                  SET last_seen=?
                  WHERE mac = ?
                  """, (datetime.now(), mac))

        conn.commit()

    # ================= PROSES NFC =================
    global last_uid

    uid = request.args.get("uid")
    mode_param = request.args.get("mode", "absen")

    if not uid:
        return "UID KOSONG!"

    app_mode = getattr(app, 'mode', 'absen')
    print(f"[SCAN] UID: {uid} | Mode ESP: {mode_param} | App Mode: {app_mode} | Waktu: {datetime.now()}")

    # ==================== FORCE RESET MODE ====================
    # Jika ESP mengirim mode=absen, paksa reset app.mode ke absen
    if mode_param == "absen" and app_mode == "register":
        app.mode = "absen"
        print("[MODE] Auto reset dari register ke absen karena ESP mengirim mode=absen")
        app_mode = "absen"

    # ==================== MODE REGISTER ====================
    if app_mode == "register":

        with get_db() as conn:
            c = conn.cursor()
            existing = c.execute("SELECT id FROM siswa WHERE uid=?", (uid,)).fetchone()

        if existing:
            return "KARTU ANDA SUDAH TERDAFTAR !"

        last_uid = uid
        print(f"[REGISTER] UID baru disimpan: {uid}")
        return "REGISTER MODE - Siap daftar di web"

    # ==================== MODE ABSENSI ====================
    # Pastikan kita di mode absen
    with get_db() as conn:
        c = conn.cursor()

        siswa = c.execute("SELECT id, nama FROM siswa WHERE uid=?", (uid,)).fetchone()
        if not siswa:
            return "KARTU TIDAK TERDAFTAR !"

        siswa_id = siswa["id"]
        nama = siswa["nama"]

        now = datetime.now()
        today = now.date()
        current_time = now.time()

        # Ambil pengaturan
        pengaturan = c.execute("""
            SELECT jam_masuk, jam_masuk_akhir, batas_telat, jam_pulang 
            FROM pengaturan LIMIT 1
        """).fetchone()

        if not pengaturan or not all(pengaturan[col] for col in ["jam_masuk", "jam_masuk_akhir", "batas_telat", "jam_pulang"]):
            return "PENGATURAN WAKTU BELUM DIISI\nHubungi Admin"

        try:
            jam_masuk       = datetime.strptime(pengaturan["jam_masuk"], "%H:%M").time()
            jam_masuk_akhir = datetime.strptime(pengaturan["jam_masuk_akhir"], "%H:%M").time()
            batas_telat     = datetime.strptime(pengaturan["batas_telat"], "%H:%M").time()
            jam_pulang      = datetime.strptime(pengaturan["jam_pulang"], "%H:%M").time()
        except Exception as e:
            print(f"[ERROR] Format jam salah: {e}")
            return "FORMAT PENGATURAN JAM SALAH\nHubungi Admin"

        record = c.execute("""
            SELECT id, waktu_masuk, waktu_pulang 
            FROM absensi 
            WHERE siswa_id = ? AND tanggal = ?
        """, (siswa_id, today)).fetchone()

        # SCAN MASUK
        if not record or record["waktu_masuk"] is None:

            if current_time < jam_masuk:
                return "BELUM WAKTUNYA ABSEN MASUK"

            if current_time > batas_telat:
                return "SUDAH LEWAT WAKTU MASUK"

            if record and record["waktu_masuk"] is not None:
                return f"{nama} ANDA SUDAH ABSEN MASUK !"

            if current_time <= jam_masuk_akhir:
                status = "hadir"
                menit_telat = 0
            else:
                status = "hadir"
                selisih = datetime.combine(today, current_time) - datetime.combine(today, jam_masuk_akhir)
                menit_telat = int(selisih.total_seconds() / 60)

            if not record:
                c.execute("""
                    INSERT INTO absensi (siswa_id, tanggal, waktu_masuk, status, menit_telat)
                    VALUES (?, ?, ?, ?, ?)
                """, (siswa_id, today, now, status, menit_telat))
            else:
                c.execute("""
                    UPDATE absensi 
                    SET waktu_masuk = ?, status = ?, menit_telat = ?
                    WHERE id = ?
                """, (now, status, menit_telat, record["id"]))

            conn.commit()

            if menit_telat > 0:
                return f"{nama} - HADIR (TELAT {menit_telat} MENIT)"
            return f"{nama} - HADIR"

        # SCAN PULANG
        elif record["waktu_pulang"] is None:

            if current_time < jam_pulang:
                return "BELUM WAKTUNYA ABSEN PULANG"

            if record and record["waktu_pulang"] is not None:
                return f"{nama} ANDA SUDAH ABSEN PULANG !"

            c.execute("UPDATE absensi SET waktu_pulang = ? WHERE id = ?", (now, record["id"]))
            conn.commit()

            return f"{nama} - PULANG BERHASIL"

        else:
            return f"{nama} ANDA SUDAH ABSEN MASUK DAN PULANG HARI INI"

    return "TERJADI KESALAHAN SISTEM"


# Route pendukung
@scan.route("/get_uid")
def get_uid():
    global last_uid
    return jsonify({"uid": last_uid})


@scan.route("/reset_uid")
def reset_uid():
    global last_uid
    last_uid = None
    return jsonify({"status": "reset"})


@scan.route("/mode")
def get_mode():
    return getattr(app, 'mode', 'absen')


@scan.route("/reset_register_mode")
def reset_register_mode():
    if hasattr(app, 'mode'):
        app.mode = "absen"
    print("[MODE] Register mode berhasil di-reset ke ABSEN")
    return "MODE RESET TO ABSEN"