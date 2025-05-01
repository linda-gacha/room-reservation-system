import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL', 'postgresql://meeting_user:password@localhost:5432/room_db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['DEBUG'] = True

db = SQLAlchemy(app)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity
        }

@app.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    return jsonify([room.to_dict() for room in rooms])

@app.route('/rooms', methods=['POST'])
def add_room():
    data = request.get_json()
    new_room = Room(name=data['name'], capacity=data['capacity'])
    db.session.add(new_room)
    db.session.commit()
    return jsonify(new_room.to_dict()), 201

@app.route('/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    room = Room.query.get_or_404(room_id)
    return jsonify(room.to_dict())

@app.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    room = Room.query.get_or_404(room_id)
    data = request.get_json()
    room.name = data['name']
    room.capacity = data['capacity']
    db.session.commit()
    return jsonify(room.to_dict())

@app.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    return jsonify({"message": "Room deleted"}), 204

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5002)
