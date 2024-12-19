from datetime import datetime
from app import app
from models import db, Message

class TestApp:
    '''Flask application in app.py'''

    def setup_method(self):
        """Set up test database and add test message before each test"""
        with app.app_context():
            # Clear any existing test messages
            test_messages = Message.query.filter(
                Message.username == "test_user"
            ).all()
            for message in test_messages:
                db.session.delete(message)
            db.session.commit()

            # Create test message
            self.test_message = Message(
                body="Test message",
                username="test_user"
            )
            db.session.add(self.test_message)
            db.session.commit()

    def teardown_method(self):
        """Clean up test database after each test"""
        with app.app_context():
            test_messages = Message.query.filter(
                Message.username == "test_user"
            ).all()
            for message in test_messages:
                db.session.delete(message)
            db.session.commit()

    def test_has_correct_columns(self):
        """Test if Message model has correct columns"""
        with app.app_context():
            message = Message.query.filter_by(username="test_user").first()
            
            assert message.body == "Test message"
            assert message.username == "test_user"
            assert isinstance(message.created_at, datetime)

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        '''returns a list of JSON objects for all messages in the database.'''
        with app.app_context():
            response = app.test_client().get('/messages')
            records = Message.query.all()

            assert response.status_code == 200
            for message in response.json:
                assert message['id'] in [record.id for record in records]
                assert message['body'] in [record.body for record in records]

    def test_creates_new_message_in_the_database(self):
        '''creates a new message in the database.'''
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={
                    "body": "New message",
                    "username": "test_user",
                }
            )

            assert response.status_code == 201
            new_message = Message.query.filter_by(body="New message").first()
            assert new_message is not None
            assert new_message.username == "test_user"

    def test_returns_data_for_newly_created_message_as_json(self):
        '''returns data for the newly created message as JSON.'''
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={
                    "body": "New message",
                    "username": "test_user",
                }
            )

            assert response.status_code == 201
            assert response.content_type == 'application/json'
            assert response.json["body"] == "New message"
            assert response.json["username"] == "test_user"

    def test_updates_body_of_message_in_database(self):
        '''updates the body of a message in the database.'''
        with app.app_context():
            message = Message.query.filter_by(username="test_user").first()
            
            response = app.test_client().patch(
                f'/messages/{message.id}',
                json={
                    "body": "Updated message",
                }
            )

            assert response.status_code == 200
            updated_message = db.session.get(Message, message.id)
            assert updated_message.body == "Updated message"

    def test_returns_data_for_updated_message_as_json(self):
        '''returns data for the updated message as JSON.'''
        with app.app_context():
            message = Message.query.filter_by(username="test_user").first()
            
            response = app.test_client().patch(
                f'/messages/{message.id}',
                json={
                    "body": "Updated message",
                }
            )

            assert response.status_code == 200
            assert response.content_type == 'application/json'
            assert response.json["body"] == "Updated message"

    def test_deletes_message_from_database(self):
        '''deletes the message from the database.'''
        with app.app_context():
            message = Message.query.filter_by(username="test_user").first()
            message_id = message.id

            response = app.test_client().delete(f'/messages/{message_id}')

            assert response.status_code == 204
            deleted_message = db.session.get(Message, message_id)
            assert deleted_message is None