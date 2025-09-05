from datetime import datetime
from database import db

class Guest(db.Model):
    __tablename__ = "guests"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)   # vip, family, friends, colleagues
    notes = db.Column(db.Text)
    rsvp_status = db.Column(db.String(20), default="pending")  # confirmed, pending, declined
    pin = db.Column(db.String(6), unique=True)
    barcode = db.Column(db.String(12), unique=True)
    invited = db.Column(db.Boolean, default=False)
    invited_at = db.Column(db.DateTime)
    checked_in = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": f"{self.first_name} {self.last_name}",
            "firstName": self.first_name,
            "lastName": self.last_name,
            "phone": self.phone,
            "category": self.category,
            "notes": self.notes,
            "rsvpStatus": self.rsvp_status,
            "pin": self.pin,
            "barcode": self.barcode,
            "invited": self.invited,
            "invitedAt": self.invited_at.isoformat() if self.invited_at else None,
            "checkedIn": self.checked_in,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

