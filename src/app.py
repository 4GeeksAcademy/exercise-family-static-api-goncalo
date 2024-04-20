"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")

jackson_family.add_member({'first_name': "Jane", "age": 35, "lucky_numbers": [10, 14, 3], "id": 1})
jackson_family.add_member({'first_name': "Jimmy", "age": 5, "lucky_numbers": [1], "id": 2})
jackson_family.add_member({'first_name': "John Jackson", "age": 33, "Lucky Numbers":[ 7, 13, 22], "id": 3})

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def handle_hello():
    # this is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    return jsonify(members), 200

@app.route('/member', methods=['POST'])
def add_member():
    # Extract data from request body
    request_data = request.json

    if not all(key in request_data for key in ('first_name', 'age', 'lucky_numbers', 'id')):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        first_name = request_data['first_name']
        age = int(request_data['age'])
        lucky_numbers = request_data['lucky_numbers']
        member_id = int(request_data['id'])
    except ValueError:
        return jsonify({"error": "Invalid data types"}), 400

    # Add new member to the family data structure
    new_member = {
        'id': member_id,
        'first_name': first_name,
        'age': age,
        'lucky_numbers': lucky_numbers
    }
    jackson_family.add_member(new_member)

    # Return success response
    return jsonify({"message": "New member added successfully", 'id': new_member['id']}), 200

@app.route('/member/<int:id>', methods=['GET'])
def get_member(id):
    # Retrieve the member from the family data structure
    member = jackson_family.get_member(id)

    # Check if the member exists
    if member is None:
        return jsonify({"error": "Member not found"}), 404

    # Construct the response dictionary
    response = {
        "id": id,
        "first_name": member["first_name"],
        "age": member["age"],
        "lucky_numbers": member["lucky_numbers"]
    }

    # Return the member's information
    return jsonify(response), 200

@app.route('/member/<int:id>', methods=['DELETE'])
def delete_member(id):
    # Delete the member from the family data structure
    success = jackson_family.delete_member(id)

    # Check if the deletion was successful
    if not success:
        return jsonify({"error": "Member not found"}), 404

    # Return success response
    return jsonify({"done": True}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
