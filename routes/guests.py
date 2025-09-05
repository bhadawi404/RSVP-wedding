import random
from flask import Blueprint, request, jsonify, send_file
from database import db
from models import Guest
import uuid
guests_bp = Blueprint("guests", __name__)
import io
import pandas as pd

# Generate PIN
def generate_pin():
    return str(random.randint(100000, 999999))

def generate_barcode():
    return str(uuid.uuid4())[:12]

# GET all guests (with filters)
@guests_bp.route("/", methods=["GET"])
def get_guests():
    search = request.args.get("search", "")
    status = request.args.get("status", "all")
    category = request.args.get("category", "all")

    query = Guest.query

    if search:
        query = query.filter(
            (Guest.first_name.ilike(f"%{search}%")) |
            (Guest.last_name.ilike(f"%{search}%")) |
            (Guest.email.ilike(f"%{search}%")) |
            (Guest.phone.ilike(f"%{search}%"))
        )

    if status != "all":
        query = query.filter(Guest.rsvp_status == status)

    if category != "all":
        query = query.filter(Guest.category == category)

    guests = query.all()
    return jsonify([g.to_dict() for g in guests])

# POST add guest
@guests_bp.route("/", methods=["POST"])
def add_guest():
    data = request.json
    new_guest = Guest(
        first_name=data["firstName"],
        last_name=data["lastName"],
        phone=data["phone"],
        category=data["category"],
        notes=data.get("notes"),
        pin=generate_pin(),
        barcode=generate_barcode()   
    )
    db.session.add(new_guest)
    db.session.commit()
    return jsonify({"message": "Guest added successfully", "guest": new_guest.to_dict()}), 201

# PUT update guest
# PUT update guest
@guests_bp.route("/<int:guest_id>", methods=["PUT"])
def update_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    data = request.json

    guest.first_name = data.get("firstName", guest.first_name)
    guest.last_name = data.get("lastName", guest.last_name)
    guest.phone = data.get("phone", guest.phone)
    guest.category = data.get("category", guest.category)
    guest.rsvp_status = data.get("rsvpStatus", guest.rsvp_status)
    guest.notes = data.get("notes", guest.notes)

    db.session.commit()
    return jsonify({"message": "Guest updated successfully", "guest": guest.to_dict()})

# DELETE guest
@guests_bp.route("/<int:guest_id>", methods=["DELETE"])
def delete_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    db.session.delete(guest)
    db.session.commit()
    return jsonify({"message": "Guest deleted successfully"})

# EXPORT guests ke Excel
@guests_bp.route("/export", methods=["GET"])
def export_guests():
    guests = Guest.query.all()
    data = [g.to_dict() for g in guests]

    # Buat DataFrame dari list of dict
    df = pd.DataFrame(data)

    # Simpan ke buffer memory sebagai Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Guests")

    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="guests.xlsx"
    )


# IMPORT guests dari Excel
@guests_bp.route("/import", methods=["POST"])
def import_guests():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    try:
        df = pd.read_excel(file)

        imported_count = 0
        for _, row in df.iterrows():
            # Cek jika email sudah ada -> skip
            if Guest.query.filter_by(email=row["email"]).first():
                continue

            guest = Guest(
                first_name=row.get("firstName", ""),
                last_name=row.get("lastName", ""),
                email=row["email"],
                phone=row.get("phone", ""),
                category=row.get("category", "friends"),
                notes=row.get("notes"),
                rsvp_status=row.get("rsvpStatus", "pending"),
                pin=generate_pin(),
                barcode=generate_barcode(),
            )
            db.session.add(guest)
            imported_count += 1

        db.session.commit()

        return jsonify({
            "message": f"{imported_count} guests imported successfully"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@guests_bp.route("/summary", methods=["GET"])
def guests_summary():
    total = Guest.query.count()
    confirmed = Guest.query.filter_by(rsvp_status="confirmed").count()
    pending = Guest.query.filter_by(rsvp_status="pending").count()
    declined = Guest.query.filter_by(rsvp_status="declined").count()

    return jsonify({
        "total": total,
        "confirmed": confirmed,
        "pending": pending,
        "declined": declined
    })