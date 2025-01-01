from datetime import datetime, timedelta
import io

from flask import Blueprint, request, jsonify, current_app, make_response, abort, send_file, render_template
import jwt

from utils import dbhelper, s3helper, misc
from config import SESSION_EXPIRE_AFTER

bl_api = Blueprint('api', __name__)

def sameret(msg:str):
    return jsonify({"result":msg})


# user
@bl_api.route("/user/login", methods=["POST"])
def user_login():
    # args
    data = request.json
    if not("username" in data and "password" in data):
        return sameret("login failed"), 400
    username = request.json["username"]
    password = request.json["password"]
    if (not username) or (not password):
        return sameret("login failed"), 400
    
    # auth
    user = dbhelper.solo_user_get(username, "auth", password)
    if not user:
        return sameret("login failed"), 400
    
    # jwt
    payload={
        "id":user["id"],
        "username":user["username"],
        "exp":datetime.utcnow() + timedelta(days=SESSION_EXPIRE_AFTER)
    }
    session = jwt.encode(payload=payload, key=current_app.config["SECRET_KEY"], algorithm="HS256")
    
    # cookie
    resp = make_response(sameret("access granted"))
    resp.set_cookie("session", session, httponly=True, samesite="Strict")
    
    # return
    return resp, 200


# download@files
@bl_api.route("/file/download/<code>", methods=["GET"])
def file_download(code:str):
    data, err = s3helper.download(code)
    if err:
        return abort(404)

    fp = io.BytesIO(data["data"])
    resp = send_file(path_or_file=fp,
                     mimetype="application/octet-stream",
                     download_name=data["filename"],
                     as_attachment=True)
    resp = make_response(resp)
    resp.headers["author"] = data["username"]
    return resp, 200


# upload@files
# need auth
@bl_api.route("/file/upload", methods=["POST"])
def file_upload():
    # auth
    user, err = misc.auth(request.cookies.get("session"), current_app.config["SECRET_KEY"])
    if err: # not login -> get out
        return sameret("no permission"), 401
    
    # args
    file = request.files.get("file")
    if not file:
        return sameret("invalid arguments"), 400
    if not file.filename:
        return sameret("invalid arguments"), 400
    data = file.stream.read()
    
    # upload
    code, err = s3helper.upload(file.filename, user, data)
    if err:
        return sameret("upload failed"), 400
    
    # return
    return {"code":code}, 200
