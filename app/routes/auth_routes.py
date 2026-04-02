from flask import Blueprint, render_template, request, redirect, session
from config import ADMIN_USERNAME, ADMIN_PASSWORD

auth = Blueprint("auth", __name__)


@auth.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["login"] = True
            return redirect("/dashboard")

        else:
            return render_template("login.html", error="Login gagal")

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    return redirect("/")