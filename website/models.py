from flask_login import UserMixin
from website import clinicDB
from datetime import datetime

# Admin (only people who log in)
class Admin(UserMixin, clinicDB.Model):
    id = clinicDB.Column(clinicDB.Integer, primary_key=True)
    admin_fullname = clinicDB.Column(clinicDB.String(150))
    admin_email = clinicDB.Column(clinicDB.String(150), unique=True, nullable=False)
    password = clinicDB.Column(clinicDB.String(255), nullable=False)
    created_at = clinicDB.Column(clinicDB.DateTime, default=datetime.utcnow)

# Editable site content (About, Achievements, etc.)
class SiteContent(clinicDB.Model):
    id = clinicDB.Column(clinicDB.Integer, primary_key=True)
    key = clinicDB.Column(clinicDB.String(100), unique=True, nullable=False)
    value = clinicDB.Column(clinicDB.Text, nullable=True)
    content_type = clinicDB.Column(clinicDB.String(50), default="text")
    is_active = clinicDB.Column(clinicDB.Boolean, default=True)
    updated_at = clinicDB.Column(clinicDB.DateTime, default=datetime.utcnow)

# Appointment bookings
class Appointment(clinicDB.Model):
    id = clinicDB.Column(clinicDB.Integer, primary_key=True)
    fullname = clinicDB.Column(clinicDB.String(150))
    email = clinicDB.Column(clinicDB.String(150))
    date = clinicDB.Column(clinicDB.Date, nullable=False)
    time = clinicDB.Column(clinicDB.Time, nullable=False)
    status = clinicDB.Column(clinicDB.String(20), default="pending")
    notes = clinicDB.Column(clinicDB.Text, nullable=True)
    created_at = clinicDB.Column(clinicDB.DateTime, default=datetime.utcnow)

# Availability calendar
class Availability(clinicDB.Model):
    id = clinicDB.Column(clinicDB.Integer, primary_key=True)
    date = clinicDB.Column(clinicDB.Date, nullable=False)
    time = clinicDB.Column(clinicDB.Time, nullable=False)
    is_available = clinicDB.Column(clinicDB.Boolean, default=True)
    __table_args__ = (clinicDB.UniqueConstraint("date", "time", name="unique_availability_slot"),)

# Audit logs (security & compliance)
class AuditLog(clinicDB.Model):
    id = clinicDB.Column(clinicDB.Integer, primary_key=True)
    admin_email = clinicDB.Column(clinicDB.String(150))
    action = clinicDB.Column(clinicDB.String(255))
    ip_address = clinicDB.Column(clinicDB.String(50))
    timestamp = clinicDB.Column(clinicDB.DateTime, default=datetime.utcnow)
