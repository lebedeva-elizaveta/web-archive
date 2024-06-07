from marshmallow import ValidationError

from app.models import User
from app.schemas import UserSchema
from app.services.security_service import EncryptionService


class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, email, password):
        user_data = {'email': email, 'password': password}
        try:
            UserSchema().load(user_data)
        except ValidationError:
            raise
        hashed_password = EncryptionService.generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        self.db.session.add(new_user)
        self.db.session.commit()
        return new_user

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and EncryptionService.check_password(user.password, password):
            return True, user.id
        return False, None

    @staticmethod
    def if_exist(email):
        existing_user = User.query.filter_by(email=email).first()
        return True if existing_user else False
