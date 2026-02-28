from flask import Blueprint, make_response, jsonify, request
from decorators import jwt_required, admin_required
from bson import ObjectId
import globals
import datetime

comments_bp = Blueprint("comments", __name__)

comments = globals.db.comments
users = globals.db.users

@comments_bp.route("/api/v1.0/posts/<string:id>/comments", methods=['GET'])
def get_all_comments(id):
    
    try:
        ObjectId(id)
    except Exception:
        return make_response( jsonify( {"error" : "Invalid post ID"} ), 400 )    
    
    data_to_return = []
    for comment in comments.find({"post_id": id}):
        comment['_id'] = str(comment['_id'])
        
        data_to_return.append(comment) 

    return make_response(jsonify(data_to_return), 200)

@comments_bp.route("/api/v1.0/posts/<string:post_id>/comment", methods=['POST'])
@jwt_required
def add_new_comment(current_user, post_id):

    try:
        ObjectId(post_id)
    except Exception:
        return make_response( jsonify( {"error" : "Invalid post ID"} ), 400 )

    
    user = users.find_one({"_id": ObjectId(current_user["sub"])})
    if not user:
        return make_response(jsonify({"error": "User not found"}), 400)
    
    data = request.get_json()
    if not data or not data.get("comment"):
        return make_response(jsonify({"error": "Comment content required"}), 400)

    new_comment = {
        "_id" : ObjectId(),
        "user_id": str(user["_id"]),
        "username" : user["username"],
        "post_id" : post_id,
        "comment" : data["comment"],
        "created_at": datetime.datetime.now()
        }
    
    result = comments.insert_one(new_comment)
    if result.inserted_id:
        return make_response( jsonify( { "message" : "Comment created" } ), 201 )
    else:
        return make_response( jsonify( { "error" : "Failed to create comment" } ), 404 )