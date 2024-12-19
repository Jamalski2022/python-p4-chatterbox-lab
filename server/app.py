from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# @app.route('/messages')
# def messages():
#     return ''

# @app.route('/messages/<int:id>')
# def messages_by_id(id):
#     return ''

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    return jsonify(
        [message.to_dict() for message in messages]
    )

@app.route('/messages', methods=['POST'])
def create_message():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('body') or not data.get('username'):
            return jsonify({
                'error': 'Both body and username are required'
            }), 400
        
        message = Message(
            body=data['body'],
            username=data['username']
        )
        db.session.add(message)
        db.session.commit()
        
        return jsonify(message.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create message',
            'details': str(e)
        }), 400

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    try:
        message = db.session.get(Message, id)
        if not message:
            return jsonify({
                'error': 'Message not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No update data provided'
            }), 400
        
        # Only allow updating specific fields
        allowed_fields = {'body', 'username'}
        for key, value in data.items():
            if key in allowed_fields:
                setattr(message, key, value)
        
        db.session.commit()
        return jsonify(message.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update message',
            'details': str(e)
        }), 400

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    try:
        message = db.session.get(Message, id)
        if not message:
            return jsonify({
                'error': 'Message not found'
            }), 404
        
        db.session.delete(message)
        db.session.commit()
        return '', 204
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete message',
            'details': str(e)
        }), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)