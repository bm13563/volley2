from api.resources.auth.auth_controller import register_controller


def add_data():
    register_controller("test_username", "test_password")
