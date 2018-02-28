from game.models import User

from . import connection


def check_connected_users():

    users = User.objects.all()
    connection.check_connected_users(users)   # Called also by 'check_connection' and 'dashboard'
