from flask import jsonify, request
from models import db, School, Event

def setup_routes(app):
    @app.route('/api/ecoles', methods=['GET'])
    def get_ecoles():
        ecoles = School.query.all()
        return jsonify([ecole.to_dict() for ecole in ecoles])

    @app.route('/api/ecoles', methods=['POST'])
    def create_ecole():
        data = request.get_json()
        new_ecole = School(name=data['name'])
        db.session.add(new_ecole)
        db.session.commit()
        return jsonify(new_ecole.to_dict()), 201

    @app.route('/api/evenements', methods=['GET'])
    def get_evenements():
        evenements = Event.query.all()
        return jsonify([event.to_dict() for event in evenements])

    @app.route('/api/evenements', methods=['POST'])
    def create_evenement():
        data = request.get_json()
        new_event = Event(title=data['title'])
        db.session.add(new_event)
        db.session.commit()
        return jsonify(new_event.to_dict()), 201

 