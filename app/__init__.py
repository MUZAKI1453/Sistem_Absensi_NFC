from flask import Flask
from config import SECRET_KEY
from .models.database import init_db

# ==========================
# MODE PERANGKAT (GLOBAL)
# ==========================

mode = "absen"
current_register = None


def create_app():

    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # buat database tabel jika belum ada
    init_db()

    from .routes.auth_routes import auth
    from .routes.dashboard_routes import dashboard
    from .routes.siswa_routes import siswa
    from .routes.scan_routes import scan
    from .routes.kelas_routes import kelas
    from .routes.log_routes import log
    from .routes.pengaturan_routes import pengaturan

    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(siswa)
    app.register_blueprint(scan)
    app.register_blueprint(kelas)
    app.register_blueprint(log)
    app.register_blueprint(pengaturan)

    return app