from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required
from website.models import Admin

auth = Blueprint("auth", __name__)

# Admin Login
@auth.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        admin_email = request.form.get("admin_email")
        password = request.form.get("password")

        current_app.logger.info(f"Attempting login for email: {admin_email}")

        admin = Admin.query.filter_by(admin_email=admin_email).first()
        

        if admin and check_password_hash(admin.password, password):
            login_user(admin, remember=True)
            flash("Welcome back, admin!", category="success")
            return redirect(url_for("views.admin_dashboard"))
        else:
            flash("Invalid email or password", category="error")

    return render_template("admin/login.html")


# Admin Logout
@auth.route("/admin/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", category="success")
    return redirect(url_for("auth.login"))


