import os
import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL', 'postgresql://meeting_user:password@localhost:5432/reservation_db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['DEBUG'] = True

db = SQLAlchemy(app)
producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, nullable=False)
    reservation_date = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'reservation_date': self.reservation_date
        }

@app.route('/reservations', methods=['GET'])
def get_reservations():
    reservations = Reservation.query.all()
    return jsonify([reservation.to_dict() for reservation in reservations])

@app.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    new_reservation = Reservation(user_id=data['user_id'], room_id=data['room_id'], reservation_date=data['reservation_date'])
    db.session.add(new_reservation)
    db.session.commit()

    # Send reservation info to Kafka topic
    producer.send('reservation-topic', new_reservation.to_dict())
    
    return jsonify(new_reservation.to_dict()), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003)
