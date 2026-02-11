from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import bcrypt
import jwt
import inspect
from functools import wraps
import datetime
from bson import ObjectId
from bson import ObjectId

app = Flask(__name__)
CORS(app)

load_dotenv()

app.config['SECRET_KEY'] = os.getenv("JWT_SECRET")

uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["hobbyhive"]
posts = db.posts
users = db.users
blacklist = db.blacklist

try:
    client.admin.command("ping")
    print("MongoDB connected successfully")
except Exception as e:
    print("MongoDB connection failed:", e)
    
def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return make_response(jsonify({'message': 'Token is missing'}), 401)
        try:
            current_user = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        except:
            return make_response(jsonify({'message': 'Token is invalid'}), 401) 
        
        sig = inspect.signature(func)
        if "current_user" in sig.parameters:
            return func(current_user,*args, **kwargs)
        bl_token = blacklist.find_one({'token': token})
        if bl_token is not None:
            return make_response(jsonify({'messgage': 'Token has been cancelled'}), 401)
        return func(*args, **kwargs)
    return jwt_required_wrapper   

def admin_required(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        token = request.headers['x-access-token']
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        if data['admin']:
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({'message': 'Admin access required'}), 401)
    return admin_required_wrapper        

@app.route('/', methods=['GET'])
def index():
    return make_response("<h1>HobbyHive Backend is running!</h1>", 200)

@app.route('/api/v1.0/posts', methods=['GET'])
def getPosts():
    data_to_return = []
    for post in posts.find():
        post['_id'] = str(post['_id'])
        data_to_return.append(post)
    return make_response(jsonify(data_to_return), 200)

@app.route('/api/v1.0/posts/create', methods=['POST'])
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

@app.route('/api/v1.0/posts/<string:id>', methods=['PUT'])
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
    
    

@app.route('/api/v1.0/posts/<string:id>', methods=['DELETE'])
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
    
@app.route("/api/v1.0/users", methods=["POST"])  
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
    
@app.route("/api/v1.0/login", methods=["GET"])
def login():
    # attempt to retrieve any exisitng authorisation
    auth = request.authorization
    if auth:
        user = users.find_one({'username': auth.username})
        if user is not None:
            if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), user['password']):
                token = jwt.encode({
                    'user' : auth.username,
                    'admin': user.get("admin", False),
                    'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
                },app.config['SECRET_KEY'], algorithm='HS256')
                return make_response(jsonify({'token' : token}), 200)   
            else:
                return make_response(jsonify({'message': 'Missing or incorrect password'}), 401)
        else:
            return make_response(jsonify({'message': 'Missing or incorrect username'}), 401)    
    return make_response(jsonify({'message': 'Authentication required'}), 401)

@app.route("/api/v1.0/logout", methods=["GET"])
@jwt_required
def logout():
    token = request.headers['x-access-token']
    blacklist.insert_one({'token': token})
    return make_response(jsonify({'message': 'Logout successful'}), 200)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)