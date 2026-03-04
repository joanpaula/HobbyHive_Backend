from flask import Blueprint, jsonify, make_response, request
import datetime
import bcrypt
import jwt
import globals
from decorators import jwt_required, admin_required

auth_bp = Blueprint("auth", __name__)

# access to users & blacklist dbs (for fetching & storing data)
users = globals.db.users
blacklist = globals.db.blacklist

# user login
@auth_bp.route("/api/v1.0/login", methods=["POST"])
def login():
    # attempt to retrieve any exisitng authorisation
    auth = request.get_json()
    # for both username and email
    identifier = auth.get("identifier", "").lower()
    # log in based on user username or email
    if auth:
        user = users.find_one({
            "$or": [
                {"username": {'$regex': f'^{identifier}$', '$options': 'i'}}, 
                {"email": identifier}
            ]}
        )
        # hash password
        if user is not None:
            if bcrypt.checkpw(
                bytes(auth.get("password", ""), "UTF-8"), user["password"]
            ):
                token = jwt.encode(
                    {
                        "sub": str(user["_id"]),
                        "user": identifier,
                        "admin": user.get("admin", False),
                        "exp": datetime.datetime.now(datetime.UTC)
                        + datetime.timedelta(minutes=30),
                    },
                    globals.secret_key,
                    algorithm="HS256",
                )
                return make_response(jsonify({"token": token}), 200)
            else:
                return make_response(
                    jsonify({"message": "Missing or incorrect password"}), 401
                )
        else:
            return make_response(
                jsonify({"message": "Missing or incorrect username"}), 401
            )
    return make_response(jsonify({"message": "Authentication required"}), 401)

# log user out
@auth_bp.route("/api/v1.0/logout", methods=["GET"])
@jwt_required
def logout():
    # send token to blacklist
    token = request.headers["x-access-token"]
    blacklist.insert_one({"token": token})
    return make_response(jsonify({"message": "Logout successful"}), 200)

# will be done later
# @auth_bp.route("/api/v1.0/forget-password", methods=["POST"])
# @jwt_required
# def forget_password():
