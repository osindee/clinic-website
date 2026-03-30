from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
from flask_login import login_required
from website.models import SiteContent, Appointment, Availability, SiteContent, Admin
from datetime import date, datetime
from website import clinicDB, mail
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from flask import jsonify
from flask import abort
from flask_login import current_user

views = Blueprint('views', __name__)

def admin_required(f):
    def wrapper(*args, **kwargs):
        if not isinstance(current_user, Admin):
            abort(403)
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# for home page 
@views.route("/")
def home():
    content = SiteContent.query.all()
    content_dict = {item.key: item.value for item in content}
      # Fetch available slots if needed
    available_slots = Availability.query.filter_by(is_available=True).all()
    slots_by_date = {}
    for slot in available_slots:
        slots_by_date.setdefault(slot.date.strftime("%Y-%m-%d"), []).append(slot.time.strftime("%H:%M"))
    today = date.today()
    return render_template("index.html", content=content_dict, slots_by_date=slots_by_date)


@views.route("/aboutus")
def aboutus():
    # Load editable content from DB
    content = SiteContent.query.all()
    content_dict = {item.key: item.value for item in content}
    return render_template("aboutus.html", content=content_dict)

@views.route("/services") 
def services():
    return render_template("services.html")

@views.route("/contact") 
def contact():
    return render_template("contact.html")

@views.route('/booking', methods=['GET', 'POST'])
def booking():
    # fetchall available slots
    available_slots = Availability.query.filter_by(is_available=True).all()
    # Group times by date (important for template logic)
    slots_by_date = {}
    for slot in available_slots:
        slots_by_date.setdefault(
            slot.date.strftime("%Y-%m-%d"), [] ).append(slot.time.strftime("%H:%M"))

    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        date_str = request.form.get("date")
        time_str = request.form.get("time")
        

        # Basic validation
        if not all([fullname, email, date_str, time_str]):
            flash("All fields except message are required.", "danger")
            return redirect(url_for("views.booking"))
        
         # Parse date and time
        try:
            date_selected = datetime.strptime(date_str, "%Y-%m-%d").date()
            time_selected = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            flash("Invalid date or time format.", "danger")
            return redirect(url_for("views.booking"))

        # Verify slot still exists & is available
        slot = Availability.query.filter_by(
            date=date_selected,
            time=time_selected,
            is_available=True
        ).first()

        if not slot:
            flash("Selected slot is no longer available.", "danger")
            return redirect(url_for("views.booking"))

        # Save appointment
        new_appointment = Appointment(
            fullname=fullname,
            email=email,
            date=date_selected,
            time=time_selected,
            status="confirmed"
        )
        clinicDB.session.add(new_appointment)

        #mark slot unavialble 
        slot.is_available = False  # lock slot
        clinicDB.session.commit()

        # Send confirmation email
        msg = Message(
            "Appointment Confirmation",
            recipients=[email]
        )
        msg.body = (
            f"Hi {fullname},\n\n"
            f"Your appointment is confirmed on "
            f"{date_selected.strftime('%B %d, %Y')} "
            f"at {time_selected.strftime('%H:%M')}.\n\n"
            f"Thank you for booking Dr. Stellah Kerong!"
        )
        mail.send(msg)

        flash("Appointment booked successfully! Check your email.", "success")
        return redirect(url_for('views.home'))
    return render_template("booking.html", slots_by_date=slots_by_date)


# ADMIN ROUTES 
@views.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_appointments = Appointment.query.count()
    upcoming_appointments = Appointment.query.filter(Appointment.date >= date.today()).count()
    available_dates_count = Availability.query.filter_by(is_available=True).count()
    return render_template("admin/dashboard.html",
                           total_appointments=total_appointments,
                           upcoming_appointments=upcoming_appointments,
                           available_dates_count=available_dates_count)


@views.route('/admin/appointments')
@login_required
@admin_required
def admin_appointments():
    appointments = Appointment.query.order_by(Appointment.date.asc()).all()
    return render_template("admin/appointments.html", appointments=appointments)

@views.route('/admin/availability', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_availability():
    if request.method == 'POST':
        date_str = request.form['date']
        time_str = request.form['time']
        is_available = 'is_available' in request.form

        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        # Limit availability to 7am–5pm
        if not (7 <= time_obj.hour <= 17):
            flash("Availability must be between 07:00 and 17:00.", "danger")
            return redirect(url_for('views.admin_availability'))

        slot = Availability.query.filter_by(date=date_obj, time=time_obj).first()

        if slot:
            slot.is_available = is_available
        else:
            slot = Availability(date=date_obj, time=time_obj, is_available=is_available)
            clinicDB.session.add(slot)

        clinicDB.session.commit()
        flash("Availability updated!", "success")
        return redirect(url_for('views.admin_availability'))

    availability = Availability.query.order_by(
        Availability.date.asc(),
        Availability.time.asc()
    ).all()

    return render_template("admin/availability.html", availability=availability)

@views.route('/admin/appointments/<int:appointment_id>/confirm', methods=['POST'])
@login_required
@admin_required
def confirm_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    appointment.status = 'confirmed'
    clinicDB.session.commit()

    # Send confirmation email to client
    try:
        msg = Message(
            subject="Your Appointment is Confirmed ✅",
            recipients=[appointment.email]
        )
        msg.body = (
            f"Hi {appointment.fullname},\n\n"
            f"Great news! Your appointment has been confirmed.\n\n"
            f"  Date : {appointment.date.strftime('%B %d, %Y')}\n"
            f"  Time : {appointment.time.strftime('%H:%M')}\n\n"
            f"Please arrive a few minutes early.\n\n"
            f"Best regards,\nDr. Stellah Kerong's Clinic"
        )
        mail.send(msg)
    except Exception as e:
        flash(f"Appointment confirmed, but email failed to send: {e}", "warning")
        return redirect(url_for('views.admin_appointments'))

    flash(f"Appointment for {appointment.fullname} confirmed and email sent.", "success")
    return redirect(url_for('views.admin_appointments'))


@views.route('/admin/appointments/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    appointment.status = 'cancelled'

    # Re-open the availability slot so others can book it
    slot = Availability.query.filter_by(
        date=appointment.date,
        time=appointment.time
    ).first()
    if slot:
        slot.is_available = True

    clinicDB.session.commit()

    # Send cancellation email to client
    try:
        msg = Message(
            subject="Your Appointment Has Been Cancelled",
            recipients=[appointment.email]
        )
        msg.body = (
            f"Hi {appointment.fullname},\n\n"
            f"We regret to inform you that your appointment scheduled for "
            f"{appointment.date.strftime('%B %d, %Y')} at {appointment.time.strftime('%H:%M')} "
            f"has been cancelled.\n\n"
            f"We apologise for the inconvenience. Please visit our website to book a new slot "
            f"at your convenience.\n\n"
            f"Best regards,\nDr. Stellah Kerong's Clinic"
        )
        mail.send(msg)
    except Exception as e:
        flash(f"Appointment cancelled, but email failed to send: {e}", "warning")
        return redirect(url_for('views.admin_appointments'))

    flash(f"Appointment for {appointment.fullname} cancelled and client notified.", "info")
    return redirect(url_for('views.admin_appointments'))


@views.route('/admin/appointments/<int:appointment_id>/complete', methods=['POST'])
@login_required
@admin_required
def complete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    notes = request.form.get('notes', '').strip()
    if not notes:
        flash("Please add session notes before marking as complete.", "danger")
        return redirect(url_for('views.admin_appointments'))

    appointment.status = 'completed'
    appointment.notes = notes          
    clinicDB.session.commit()

    flash(f"Appointment for {appointment.fullname} marked as completed.", "success")
    return redirect(url_for('views.admin_appointments'))
