from flask import Blueprint, make_response, redirect, render_template, request, current_app

from utils import misc

bl_front = Blueprint("front", __name__)


@bl_front.route("/", methods=["GET"])
def index():
    user, err = misc.auth(request.cookies.get("session"), current_app.config["SECRET_KEY"])
    if err: # not login -> go login
        return redirect("/login")
    
    return render_template("index.html", username=user["username"])


@bl_front.route("/login", methods=["GET"])
def login():
    user, err = misc.auth(request.cookies.get("session"), current_app.config["SECRET_KEY"])
    if err: # not login -> go login
        return render_template("login.html")
    return redirect("/") # logined -> go index


@bl_front.route("/logout", methods=["GET"])
def logout():
    resp = make_response(redirect("/"))
    resp.set_cookie("session", "", httponly=True, samesite="Strict")
    return resp, 200
