from flask import redirect, render_template, request, url_for, session, send_file, flash
from flask_login import current_user, login_user, logout_user, login_required
from functools import wraps
from io import BytesIO

from app.modules.auth import auth_bp
from app.modules.auth.forms import LoginForm, SignupForm, TwoFactorForm
from app.modules.auth.services import AuthenticationService
from app.modules.profile.services import UserProfileService

# Importamos User, ROLES y db para el panel de admin
from app.modules.auth.models import User, ROLES
from app import db


authentication_service = AuthenticationService()
user_profile_service = UserProfileService()


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            flash("No tienes permisos para acceder a esta página.", "danger")
            return redirect(url_for("public.index"))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if not authentication_service.is_email_available(email):
            return render_template("auth/signup_form.html", form=form, error=f"Email {email} in use")

        try:
            user = authentication_service.create_with_profile(**form.data)
        except Exception as exc:
            return render_template("auth/signup_form.html", form=form, error=f"Error creating user: {exc}")

        login_user(user, remember=True)
        return redirect(url_for("public.index"))

    return render_template("auth/signup_form.html", form=form)



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        result = authentication_service.login(form.email.data, form.password.data, remember=form.remember_me.data)

        if result == True:
            return redirect(url_for("public.index"))

        if result == "otp_required":
            user = authentication_service.repository.get_by_email(form.email.data)
            session["pre_2fa_user_id"] = user.id
            session["remember_me"] = form.remember_me.data
            return redirect(url_for("auth.two_factor_verify"))

        return render_template("auth/login_form.html", form=form, error="Invalid credentials")

    return render_template("auth/login_form.html", form=form)



@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.index"))



@auth_bp.route("/2fa/verify", methods=["GET", "POST"])
def two_factor_verify():
    form = TwoFactorForm()
    user_id = session.get("pre_2fa_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = authentication_service.repository.get_by_id(user_id)
    if request.method == "POST" and form.validate_on_submit():
        token = form.token.data.strip()
        if user and user.verify_totp(token):
            login_user(user, remember=session.get("remember_me", False))
            session.pop("pre_2fa_user_id", None)
            session.pop("remember_me", None)
            return redirect(url_for("public.index"))
        flash("Invalid authentication code", "danger")

    return render_template("auth/2fa_verify.html", form=form)

@auth_bp.route("/2fa/setup", methods=["GET", "POST"])
def two_factor_setup():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    user = current_user
    form = TwoFactorForm()

    if not getattr(user, "totp_secret", None):
        import pyotp
        secret = pyotp.random_base32()
        user.totp_secret = secret

    user.two_factor_enabled = False
    authentication_service.repository.session.add(user)
    authentication_service.repository.session.commit()

    import pyotp
    uri = pyotp.totp.TOTP(user.totp_secret).provisioning_uri(name=user.email, issuer_name="Games Hub")

    return render_template("auth/2fa_setup.html", uri=uri, secret=user.totp_secret, form=form)



@auth_bp.route("/2fa/qrcode")
def two_factor_qrcode():
    if not current_user.is_authenticated:
        return ("", 401)

    user = current_user
    if not getattr(user, "totp_secret", None):
        return ("No 2FA secret configured", 404)

    import qrcode
    import pyotp

    uri = pyotp.totp.TOTP(user.totp_secret).provisioning_uri(name=user.email, issuer_name="Games Hub")
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")



@auth_bp.route("/2fa/confirm", methods=["POST"])
def two_factor_confirm():
    if not current_user.is_authenticated:
        return ("", 401)

    form = TwoFactorForm()
    if form.validate_on_submit():
        token = form.token.data.strip()
        user = current_user
        if user.verify_totp(token):
            user.two_factor_enabled = True
            authentication_service.repository.session.add(user)
            authentication_service.repository.session.commit()
            flash("Two-factor authentication enabled.", "success")
            return redirect(url_for("profile.edit_profile"))

        flash("Invalid authentication code.", "danger")

    return redirect(url_for("auth.two_factor_setup"))



@auth_bp.route("/admin/users", methods=["GET"])
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("auth/admin_users.html", users=users, roles=ROLES)


@auth_bp.route("/admin/users/<int:user_id>/role", methods=["POST"])
@admin_required
def change_user_role(user_id):
    new_role = request.form.get("role")

    if new_role not in ROLES:
        flash("Rol inválido", "danger")
        return redirect(url_for("auth.admin_users"))

    user = User.query.get_or_404(user_id)
    user.role = new_role
    db.session.commit()

    flash(f"Rol de {user.email} actualizado a {new_role}", "success")
    return redirect(url_for("auth.admin_users"))
