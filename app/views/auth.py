from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import AuthForm
from ..functions import generate_id, generate_string, get_base64_encode
from ..app_functions import get_login, user_login_required
from ..db import User, db
from flask_login import login_user

auth = Blueprint('auth', __name__)

@auth.route("/", methods=("GET", "POST"))
def auth_index():
    if get_login():
        return redirect(url_for("home.home_index"))

    form = AuthForm(request.form)

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        data = User.query.filter(User.email == email).first()

        if data:
            if check_password_hash(data.password, password):
                session.permanent = True
                session["session-sign-id"] = get_base64_encode(data.session_id)
                login_user(data)
                return redirect(url_for("home.home_index"))
            else:
                flash("Incorrect password for entered email account!", "red")
        else:
            hashed_password = generate_password_hash(password, "SHA256")
            name = email.split("@")[0][:18]
            user = User(
                name=name,
                email=email,
                password=hashed_password,
                session_id=generate_id(name, email, hashed_password)
            )

            db.session.add(user)
            db.session.commit()

            flash("New account has been created, enter credentials to sign in.", "green")

        return redirect(url_for(".auth_index"))

    return render_template(
        "auth/index.html",
        title="Login",
        form=form
    )

@auth.route("/logout", methods=["GET", "POST"])
@user_login_required
def logout():
    if "session-sign-id" in session:
        session.pop("session-sign-id")
    session.permanent = False
    return redirect(url_for(".auth_index"))
