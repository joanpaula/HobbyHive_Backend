from flask import Blueprint, make_response, jsonify, request
from decorators import jwt_required, admin_required
from bson import ObjectId
import globals
import datetime

likes_bp = Blueprint("likes", __name__)

likes = globals.db.likes
users = globals.db.users
posts = globals.db.posts

@likes_bp.route("/api/v1.0/posts/<string:post_id>/like", methods=["PUT"])
@jwt_required
def toggle_like(current_user, post_id):
    
    try:
        post_obj_id = ObjectId(post_id)
    except Exception:
        return make_response (jsonify({"error": "Invalid post ID"}), 400)
    
    user_id = str(current_user["sub"])
    
    existing_like = likes.find_one({
        "user_id": user_id,
        "post_id": post_id
    })
    
    if existing_like:
        likes.delete_one({"_id": existing_like["_id"]})
        posts.update_one({"_id": post_obj_id}, {"$inc": {"likes_count": -1}})
        liked = False
    else:
        like_doc = {
            "_id": ObjectId(),
            "user_id": user_id,
            "post_id" : post_id,
            "created_at": datetime.datetime.now()
        }
        likes.insert_one(like_doc)
        posts.update_one({"_id": post_obj_id}, {"$inc": {"likes_count": 1}})
        liked = True
        
    post = posts.find_one({"_id": post_obj_id})
    likes_count = post.get("likes_count", 0)
    
    return make_response( jsonify( { "liked" : liked, "likes_count": likes_count } ), 200 )