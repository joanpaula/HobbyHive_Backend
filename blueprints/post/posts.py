from flask import Blueprint, jsonify, make_response, request
import datetime
import globals
from bson import ObjectId
from bson import ObjectId
from decorators import jwt_required, admin_required
import boto3
from botocore.exceptions import ClientError
import globals
import uuid

posts_bp = Blueprint("posts", __name__)

posts = globals.db.posts

AWS_ACCESS_KEY=globals.aws_access_key
AWS_SECRET_KEY=globals.aws_secret_key
AWS_S3_BUCKET_NAME=globals.aws_s3_bucket_name
AWS_REGION=globals.aws_region

s3_client = boto3.client(
            service_name = "s3",
            region_name = AWS_REGION,
            aws_access_key_id = AWS_ACCESS_KEY,
            aws_secret_access_key = AWS_SECRET_KEY
        )

def get_presigned_get_url(key: str) -> str:
    try:
        return s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": AWS_S3_BUCKET_NAME, 
                    "Key": key},
            ExpiresIn=3600
        )
    except ClientError:
        return ""

@posts_bp.route('/api/v1.0/presign-url', methods=['POST'])
def generate_presigned_url():
    data = request.get_json()
    filename = data.get("filename")
    content_type = data.get("contentType")
    
    if not filename:
        return make_response(jsonify({"error": "Missing filename in request body"}), 400)
    
    if not content_type:
        return make_response(jsonify({"error": "Missing content_type in request body"}), 400)
    
    key = f"uploads/{uuid.uuid4()}_{filename}"
    
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": AWS_S3_BUCKET_NAME, 
                    "Key": key, 
                    "ContentType": content_type},
            ExpiresIn=3600
        )

        return jsonify({
            "uploadUrl": url,
            "key": key})
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

@posts_bp.route('/api/v1.0/posts', methods=['GET'])
def getPosts():
    data_to_return = []
    for post in posts.find():
        post['_id'] = str(post['_id'])
        
        if "media_url" in post:
            post["media_url"] = [
                get_presigned_get_url(k) for k in post["media_url"]
            ]
        
        data_to_return.append(post)
    return make_response(jsonify(data_to_return), 200)

@posts_bp.route('/api/v1.0/posts/create', methods=['POST'])
def createPost():

    required = ["body_text"]
    missing = [f for f in required if f not in request.form]

    if missing:
        return make_response( jsonify({"error":"Missing fields required: " + ", ".join(missing)} ), 400)
    
    media_keys = [m for m in request.form.getlist("media_url") if m] 
    
    new_post = {
        "user_id": str(ObjectId()),
        "username": request.form["username"],
        "body_text": request.form["body_text"],
        "image": request.form.get("image", None),
        "created_at": datetime.datetime.utcnow().isoformat() + 'Z'
    }
    
    if media_keys:
        new_post["media_url"] = media_keys

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