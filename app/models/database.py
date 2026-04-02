import sqlite3
from config import DB_NAME


def get_db():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # ======================
        # TABEL KELAS
        # ======================
        c.execute("""
        CREATE TABLE IF NOT EXISTS kelas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_kelas TEXT NOT NULL UNIQUE
        )
        """)

        # ======================
        # TABEL SISWA
        # ======================
        c.execute("""
        CREATE TABLE IF NOT EXISTS siswa(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            nis TEXT NOT NULL UNIQUE,
            uid TEXT NOT NULL UNIQUE,
            kelas_id INTEGER,
            FOREIGN KEY (kelas_id) REFERENCES kelas(id) ON DELETE SET NULL
        )
        """)

        # ======================
        # TABEL ABSENSI
        # ======================
        c.execute("""
        CREATE TABLE IF NOT EXISTS absensi(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            siswa_id INTEGER NOT NULL,
            tanggal DATE DEFAULT CURRENT_DATE,
            status TEXT CHECK(status IN ('hadir','telat','sakit','izin','alfa')) DEFAULT 'hadir',
            waktu DATETIME DEFAULT CURRENT_TIMESTAMP,
            menit_telat INTEGER DEFAULT 0,
            FOREIGN KEY (siswa_id) REFERENCES siswa(id) ON DELETE CASCADE
        )
        """)

        # ======================
        # INDEX 
        # ======================
        c.execute("""
        CREATE INDEX IF NOT EXISTS idx_absensi_siswa_tanggal
        ON absensi(siswa_id, tanggal)
        """)

        # ======================
        # TABEL PENGATURAN
        # ======================
        c.execute("""
        CREATE TABLE IF NOT EXISTS pengaturan(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jam_masuk TEXT,
            batas_telat TEXT,
            jam_pulang TEXT
        )
        """)

        conn.commit()