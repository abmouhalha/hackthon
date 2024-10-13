from flask import jsonify, request
from models import db, School, Event

# Fonction pour récupérer toutes les écoles
def get_ecoles():
    ecoles = School.query.all()
    return jsonify([ecole.to_dict() for ecole in ecoles])

# Fonction pour créer une nouvelle école
def create_ecole():
    data = request.get_json()
    new_ecole = School(name=data['name'])
    db.session.add(new_ecole)
    db.session.commit()
    return jsonify(new_ecole.to_dict()), 201

# Fonction pour récupérer tous les événements
def get_evenements():
    evenements = Event.query.all()
    return jsonify([event.to_dict() for event in evenements])

# Fonction pour créer un nouvel événement
def create_evenement():
    data = request.get_json()
    new_event = Event(title=data['title'])
    db.session.add(new_event)
    db.session.commit()
    return jsonify(new_event.to_dict()), 201

# Route to make a reservation
@app.route('/api/reservations', methods=['POST'])
def make_reservation():
    data = request.get_json()
    user_id = data.get('user_id')
    event_id = data.get('event_id')
    
    if not user_id or not event_id:
        return jsonify({'error': 'user_id and event_id are required'}), 400

    # Load user data
    users = load_data().get('users', [])
    user = next((u for u in users if u['id'] == user_id), None)
    if user is None:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Load event data
    events = load_data().get('evenements', [])
    event = next((e for e in events if e['id'] == event_id), None)
    if event is None:
        return jsonify({'error': 'Événement non trouvé'}), 404

    # Add event to user's history
    user['historique_evenements'].append({
        'id_evenement': event['id'],
        'nom_evenement': event['nom'],
        'date': event['date']
    })

    # Optionally save updated user data back to data.json if needed
    # Save data back to data.json
    with open('data.json', 'r+', encoding='utf-8') as f:
        content = json.load(f)
        for i, u in enumerate(content['users']):
            if u['id'] == user_id:
                content['users'][i] = user
                break
        f.seek(0)
        json.dump(content, f, ensure_ascii=False, indent=4)

    return jsonify({"message": "Réservation réussie!", "event": event}), 201
# Route to get all events
@app.route('/api/evenements', methods=['GET'])
def get_events():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify(data['evenements']), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
