from flask import Blueprint, jsonify, make_response, request
import globals
from botocore.exceptions import ClientError
import globals

hobbies_bp = Blueprint("hobbies", __name__)

# access to hobbies db
hobbies = globals.db.hobbies

# fetch all hobbies
@hobbies_bp.route('/api/v1.0/hobbies', methods=['GET'])
def get_all_hobbies():
    
    data_to_return = []
    for hobby in hobbies.find():
        hobby['_id'] = str(hobby['_id'])
        
        data_to_return.append(hobby)
    return make_response(jsonify(data_to_return), 200)