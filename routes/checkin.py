from flask import Blueprint, request, jsonify
from database import db
from models import Guest
checkin_bp = Blueprint("checkin", __name__,)

# ✅ Check-in by Barcode / QR Code
@checkin_bp.route("/barcode", methods=["POST"])
def checkin_barcode():
    data = request.get_json()
    code = data.get("barcode")

    if not code:
        return jsonify({"success": False, "message": "Barcode/QR code is required"}), 400

    guest = Guest.query.filter_by(barcode=code).first()
    if not guest:
        return jsonify({"success": False, "message": "Guest not found"}), 404

    if guest.rsvp_status == "declined":
        return jsonify({
            "success": False,
            "message": f"{guest.name} has declined the invitation and cannot check in",
            "guest": guest.to_dict()
        }), 403

    if guest.checked_in:
        return jsonify({
            "success": False,
            "message": f"{guest.name} already checked in",
            "guest": guest.to_dict()
        }), 200

    # Jika status pending atau confirmed tapi belum check-in
    guest.checked_in = True
    guest.rsvp_status = "confirmed"
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"{guest.name} checked in successfully!",
        "guest": guest.to_dict()
    }), 200


# ✅ Check-in by PIN
@checkin_bp.route("/pin", methods=["POST"])
def checkin_pin():
    data = request.get_json()
    pin = data.get("pin")

    if not pin:
        return jsonify({"success": False, "message": "PIN code is required"}), 400

    guest = Guest.query.filter_by(pin=pin).first()
    if not guest:
        return jsonify({"success": False, "message": "Guest not found"}), 404

    if guest.rsvp_status == "declined":
        return jsonify({
            "success": False,
            "message": f"{guest.name} has declined the invitation and cannot check in",
            "guest": guest.to_dict()
        }), 403

    if guest.checked_in:
        return jsonify({
            "success": False,
            "message": f"{guest.name} already checked in",
            "guest": guest.to_dict()
        }), 200

    guest.checked_in = True
    guest.rsvp_status = "confirmed"
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"{guest.name} checked in successfully with PIN!",
        "guest": guest.to_dict()
    }), 200



# ✅ Guest Statistics for Dashboard
@checkin_bp.route("/stats", methods=["GET"])
def guests_stats():
    total = Guest.query.count()
    checked_in = Guest.query.filter_by(checked_in=True).count()
    remaining = total - checked_in
    rate = round((checked_in / total * 100), 2) if total > 0 else 0

    return jsonify({
        "expected": total,
        "checked_in": checked_in,
        "remaining": remaining,
        "rate": f"{rate}%"
    })
