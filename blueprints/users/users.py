from flask import Blueprint, jsonify, make_response, request
import globals
import bcrypt
from bson import ObjectId
from bson import ObjectId
from decorators import jwt_required, admin_required

users_bp = Blueprint("users", __name__)

users = globals.db.users

@users_bp.route("/api/v1.0/users", methods=["POST"])  
def add_new_user():

    required = ["name", "username", "password", "email"]
    missing = [f for f in required if f not in request.form]

    if missing:
        return make_response( jsonify({"error":"Missing fields required: " + ", ".join(missing)} ), 400)

    new_user = {
        "_id" : ObjectId(),
            "name" : request.form["name"],
            "username" : request.form["username"],  
            "password" : request.form["password"],
            "email" : request.form["email"],
            # "admin" : request.form["admin"].lower() == "true"
            "admin": False
    }    
    new_user["password"] = bcrypt.hashpw(new_user["password"].encode('utf-8'), bcrypt.gensalt())
    new_user_id = users.insert_one(new_user)
    new_user_link = "http://localhost:5000/api/v1.0/users/" + str(new_user_id.inserted_id)
    return make_response( jsonify( {"url": new_user_link} ), 201)