from flask import Flask
from database import db, migrate
from routes.guests import guests_bp
from routes.checkin import checkin_bp
from dotenv import load_dotenv
import os

# Import models agar terbaca migrasi
from models import Guest
from flask_cors import CORS
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # CORS(app, resources={r"/api/*": {"origins": "http://localhost:8081"}})
    # Register blueprints
    app.register_blueprint(guests_bp, url_prefix="/api/guests")
    app.register_blueprint(checkin_bp, url_prefix="/api/checkin")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
