from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from models import db
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initializing Flask-Migrate
CORS(app)  # Enable CORS if needed

# Function to load data from data.json file
def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "File not found"}
    except json.JSONDecodeError:
        return {"error": "Error parsing JSON"}

# Route to get all schools
@app.route('/api/ecoles', methods=['GET'])
def get_ecoles():
    data = load_data()
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data.get('ecoles', []))

# Route to get all events
@app.route('/api/evenements', methods=['GET'])
def get_evenements():
    data = load_data()
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data.get('evenements', []))

# Route to get a school by ID
@app.route('/api/ecoles/<int:id>', methods=['GET'])
def get_ecole_by_id(id):
    data = load_data()
    if "error" in data:
        return jsonify(data), 500
    ecoles = data.get('ecoles', [])
    ecole = next((ecole for ecole in ecoles if ecole['id'] == id), None)
    if ecole:
        return jsonify(ecole)
    return jsonify({'error': 'École non trouvée'}), 404

# Route to make a reservation
@app.route('/api/reservations', methods=['POST'])
def make_reservation():
    data = request.get_json()
    return jsonify({"message": "Réservation réussie!", "data": data}), 201

# Route to get teachers from a school by ID
@app.route('/api/ecoles/<int:id>/professeurs', methods=['GET'])
def get_professeurs_by_ecole(id):
    data = load_data()
    if "error" in data:
        return jsonify(data), 500
    ecoles = data.get('ecoles', [])
    ecole = next((ecole for ecole in ecoles if ecole['id'] == id), None)
    if ecole:
        professeurs = []
        for classe in ecole.get('classes', []):
            professeurs.extend(classe.get('professeurs', []))
        return jsonify(professeurs)
    return jsonify({'error': 'École non trouvée'}), 404

# Route to get classes of a school by ID
@app.route('/api/ecoles/<int:id>/classes', methods=['GET'])
def get_classes_by_ecole(id):
    data = load_data()
    if "error" in data:
        return jsonify(data), 500
    ecoles = data.get('ecoles', [])
    ecole = next((ecole for ecole in ecoles if ecole['id'] == id), None)
    if ecole:
        return jsonify(ecole.get('classes', []))
    return jsonify({'error': 'École non trouvée'}), 404

# Route to create an event
@app.route('/api/evenements', methods=['POST'])
def create_evenement():
    data = request.get_json()
    try:
        with open('data.json', 'r+', encoding='utf-8') as f:
            content = json.load(f)
            data['id'] = len(content['evenements']) + 1  # Assign new ID
            content['evenements'].append(data)
            f.seek(0)
            json.dump(content, f, ensure_ascii=False, indent=4)
        return jsonify({"message": "Événement créé!", "data": data}), 201
    except FileNotFoundError:
        return jsonify({'error': 'Fichier data.json non trouvé'}), 500
    except json.JSONDecodeError:
        return jsonify({'error': 'Erreur lors du traitement des données JSON'}), 500

# Route to get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    data = load_data()
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data.get('users', []))

# Route to get user by ID
@app.route('/api/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    data = load_data()
    if "error" in data:
        return jsonify(data), 500
    users = data.get('users', [])
    user = next((user for user in users if user['id'] == id), None)
    if user:
        return jsonify(user)
    return jsonify({'error': 'Utilisateur non trouvé'}), 404

# Route to suggest events for a user
@app.route('/api/suggest_events/<int:user_id>', methods=['GET'])
def suggest_events(user_id):
    data = load_data()
    if "error" in data:
        return jsonify(data), 500
    
    users = data.get('users', [])
    user = next((u for u in users if u['id'] == user_id), None)
    if user is None:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    suggested_events = []
    
    # Simple suggestion logic
    for event in data['evenements']:
        score = 0
        
        # Check interests
        if any(tag in event['tags'] for tag in user['interets']):
            score += 2
        
        # Check historical events
        if any(hist['id_evenement'] == event['id'] for hist in user['historique_evenements']):
            score += 1

        if score > 0:
            suggested_events.append({**event, 'score': score})
    
    # Sort events by score
    suggested_events.sort(key=lambda x: x['score'], reverse=True)
    
    # If no suggested events, return all events
    if not suggested_events:
        return jsonify(data['evenements']), 200  # Return all events if none are suggested

    return jsonify(suggested_events), 200

if __name__ == '__main__':
    app.run(debug=True)
