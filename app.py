from flask import Flask
from flask_cors import CORS
import globals
from blueprints.users.users import users_bp
from blueprints.post.posts import posts_bp
from blueprints.auth.auth import auth_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(posts_bp)
app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)

try:
    globals.client.admin.command("ping")
    print("MongoDB connected successfully")
except Exception as e:
    print("MongoDB connection failed:", e)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)