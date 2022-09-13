from os import abort
from passlib.hash import sha256_crypt

from api.db import dbm
from api.resources.auth.auth_utils import password_matches, generate_token
from common.logging import get_logger


logger = get_logger()


def register_controller(username, password):
    encrypted_password = sha256_crypt.encrypt(password)
    try:
        dbm.execute(
            """
                insert into users (username, password)
                values (%(username)s, %(password)s)
            """,
            {"username": username, "password": encrypted_password},
        )
    except Exception as e:
        logger.error(
            "could not register user", extra={"username": username, "error": e}
        )
        raise (e)


def login_controller(username, hashed_password):
    user = password_matches(username, hashed_password)

    if user:
        return generate_token(str(user.get("user_id")))
    else:
        abort(401, "invalid username or password")
