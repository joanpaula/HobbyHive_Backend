from flask import Blueprint, jsonify, make_response, request
import globals
import bcrypt
from bson import ObjectId
from bson import ObjectId
from decorators import jwt_required, admin_required
import datetime

users_bp = Blueprint("users", __name__)

# access to posts, comments, annd users dbs (for fetching & storing data)
users = globals.db.users
posts = globals.db.posts
comments = globals.db.comments

# create new user (signup)
@users_bp.route("/api/v1.0/signup", methods=["POST"])  
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
            "admin": False,
            "created_at": datetime.datetime.utcnow().isoformat() + 'Z'
    }    
    # hash password
    new_user["password"] = bcrypt.hashpw(new_user["password"].encode('utf-8'), bcrypt.gensalt())
    new_user_id = users.insert_one(new_user)
    new_user_link = "http://localhost:5000/api/v1.0/users/" + str(new_user_id.inserted_id)
    return make_response( jsonify( {"url": new_user_link} ), 201)

# retrieve user details
@users_bp.route("/api/v1.0/users/<string:id>", methods=["GET"])
@jwt_required
def get_one_user(id):
    
    try:
        ObjectId(id)
    except Exception:
        return make_response( jsonify( {"error" : "Invalid user ID"} ), 400 )    

    user = users.find_one({ "_id" : ObjectId(id) })
    if user is None:
        return make_response(jsonify({"error": "User not found"}), 404)
    user['_id'] = str(user['_id'])

    for key, value in user.items():
            if isinstance(value, bytes):
                user[key] = value.decode('utf-8')

    return make_response(jsonify(user), 200)

# edit user details
@users_bp.route("/api/v1.0/users/<string:id>", methods=["PUT"])
@jwt_required
def edit_user_profile(id):
    
    try:
        ObjectId(id)
    except Exception:
        return make_response(jsonify({"error": "Invalid user ID"}), 400)
    
    data = request.get_json()

    update_fields = {}

    if "name" in data and data["name"].strip() != "":
        update_fields["name"] = data["name"]
        
    if "username" in data and data["username"].strip() != "":
        update_fields["username"] = data["username"]
        
    if "email" in data and data["email"].strip() != "":
        update_fields["email"] = data["email"]
        
    if "password" in data and data["password"].strip() != "":
        data["password"] = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())    
        update_fields["password"] = data["password"]        

    if not update_fields:
        return make_response(jsonify({"message": "No fields to update"}), 400)

    result = users.update_one({"_id": ObjectId(id)}, {"$set": update_fields})

    if result.matched_count == 1:
        if "username" in update_fields:
            posts.update_many({"user_id": id}, {"$set": {"username": update_fields["username"]}})
            comments.update_many({"user_id": id}, {"$set": {"username": update_fields["username"]}})
        return make_response(jsonify({"message": "Profile updated successfully"}), 201)
    else:
        return make_response(jsonify({"message": "profile not found"}), 404)
  
# delete user profile 
@users_bp.route("/api/v1.0/users/<string:id>", methods=["DELETE"]) 
@jwt_required 
def delete_user(current_user, id):

    try:
        ObjectId(id)
    except Exception:
        return make_response( jsonify( {"error" : "Invalid user ID"} ), 400 )  
    
    user = users.find_one({ "_id" : ObjectId(id) })
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)

    # if (user["username"] != current_user["user"] and current_user["admin"] is not True):
    #     return make_response(jsonify({"error":"You have no authority to delete this user"}), 403)     

    result = users.delete_one( { "_id" : ObjectId(id) } )
    if result.deleted_count == 1:
        return make_response( jsonify( {} ), 204)    