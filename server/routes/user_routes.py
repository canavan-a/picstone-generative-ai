from flask import Blueprint
from controllers.user_controller import UserController

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    return UserController.get_users()

