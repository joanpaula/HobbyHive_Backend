from flask import Flask
from flask_cors import CORS
import globals
from blueprints.users.users import users_bp
from blueprints.post.posts import posts_bp
from blueprints.auth.auth import auth_bp
from blueprints.places.places import places_bp
from blueprints.comments.comments import comments_bp
from blueprints.likes.likes import likes_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(posts_bp)
app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(places_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(likes_bp)

try:
    globals.client.admin.command("ping")
    print("MongoDB connected successfully")
except Exception as e:
    print("MongoDB connection failed:", e)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)