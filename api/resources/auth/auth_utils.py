from os import environ
from jwt import encode, decode
from uuid import uuid4
from functools import wraps

from passlib.hash import sha256_crypt
from flask import request, abort

from api.db import dbm
from common.logging import get_logger


logger = get_logger()


def generate_token(user_id):
    try:
        token = encode(
            {"user_id": user_id, "exp": environ.get("JWT_EXPIRATION")},
            environ.get("SECRET_KEY"),
        )
        logger.info("token generated", extra={"user_id": user_id})
        return token
    except Exception as e:
        logger.error("could not generate token", extra={"error": e})
        raise (e)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if token is None:
            logger.error("token is missing")
            abort(401, "token is missing")

        try:
            data = decode(token, environ.get("SECRET_KEY"))
            current_user = get_user_by_id(data.get("user_id"))
        except Exception as e:
            logger.error("token is invalid", extra={"error": e})
            abort(401, "token is invalid")

        return f(*args, **kwargs)

    return decorated


def get_user_by_id(user_id):
    logger.info("getting user by id", extra={"user_id": user_id})
    return dbm.fetch_one(
        """
        select *
        from users
        where user_id = %(user_id)s
    """,
        {"user_id": user_id},
    )


def get_user_by_username(username):
    logger.info("getting user by username", extra={"username": username})
    return dbm.fetch_one(
        """
        select *
        from users
        where username = %(username)s
    """,
        {"username": username},
    )


def password_matches(username, hashed_password):
    user = get_user_by_username(username)

    if not user:
        logger.error("invalid username", extra={"username": username})
        abort(401, "invalid username")
    elif not sha256_crypt.verify(hashed_password, user.get("password") or uuid4()):
        logger.error("invalid password", extra={"username": username})
        abort(401, "invalid password")
    else:
        logger.info("user authenticated", extra={"username": username})
        return user
