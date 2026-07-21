from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required

from splent_framework.utils.form_helpers import form_error, form_success

from app.features.auth.services import AuthenticationService
from app.features.profile import profile_bp
from app.features.profile.forms import UserProfileForm
from app.features.profile.services import UserProfileService

authentication_service = AuthenticationService()
user_profile_service = UserProfileService()


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = authentication_service.get_authenticated_user_profile()
    if not profile:
        return redirect(url_for("public.index"))

    form = UserProfileForm()
    if request.method == "POST":
        result, errors = user_profile_service.update_profile(profile.id, form)
        if errors:
            return form_error("profile/edit.html", form, errors)
        return form_success("profile.edit_profile", "Profile updated successfully")

    return render_template("profile/edit.html", form=form)


@profile_bp.route("/profile/summary")
@login_required
def my_profile():
    page = request.args.get("page", 1, type=int)
    summary = user_profile_service.summary_for_user(current_user.id, page)
    return render_template(
        "profile/summary.html",
        user_profile=current_user.profile,
        user=current_user,
        **summary,
    )
