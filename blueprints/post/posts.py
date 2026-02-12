from flask import Blueprint, jsonify, make_response, request
import datetime
import globals
from bson import ObjectId
from bson import ObjectId
from decorators import jwt_required, admin_required

posts_bp = Blueprint("posts", __name__)

posts = globals.db.posts

@posts_bp.route('/api/v1.0/posts', methods=['GET'])
def getPosts():
    data_to_return = []
    for post in posts.find():
        post['_id'] = str(post['_id'])
        data_to_return.append(post)
    return make_response(jsonify(data_to_return), 200)

@posts_bp.route('/api/v1.0/posts/create', methods=['POST'])
def createPost():

    # required = ["username", "body_text"]
    required = ["body_text"]
    missing = [f for f in required if f not in request.form]

    if missing:
        return make_response( jsonify({"error":"Missing fields required: " + ", ".join(missing)} ), 400)
    
    new_post = {
        "user_id": str(ObjectId()),
        "username": request.form["username"],
        "body_text": request.form["body_text"],
        "media_url": request.form.getlist("media_url"),
        "image": request.form.get("image", None),
        "created_at": datetime.datetime.utcnow().isoformat() + 'Z'
    }

    new_post_id = posts.insert_one(new_post)
    return make_response(jsonify({"message": "Post created", "post_id": str(new_post_id.inserted_id)}), 201)

@posts_bp.route('/api/v1.0/posts/<string:id>', methods=['PUT'])
def edit_post(id):
    
    try:
        ObjectId(id)
    except Exception:
        return make_response( jsonify( {"error" : "Invalid post ID"} ), 400 )    
    
    data = request.get_json()
    
    update_fields = {}
    
    if 'body_text' in data and data['body_text'].strip() != "":
        update_fields['body_text'] = data['body_text']     
                
    if not update_fields:
        return make_response( jsonify( {"message" : "No fields to update"} ), 400 )
    
    result = posts.update_one({"_id": ObjectId(id)}, {"$set": update_fields})
    
    if result.matched_count == 1:
        return make_response( jsonify( {"message": "Post updated successfully"} ), 201)
    else:
        return make_response( jsonify( {"message":"post not found"} ), 404)
    
@posts_bp.route('/api/v1.0/posts/<string:id>', methods=['DELETE'])
def delete_post(id):

    try:
        ObjectId(id)
    except Exception:
        return make_response( jsonify( {"error" : "Invalid post ID"} ), 400 )    

    result = posts.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return make_response( jsonify( {"message": "Post deleted successfully"} ), 204)
    else:
        return make_response( jsonify( {"message":"post not found"} ), 404)