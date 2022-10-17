import base64
import json
import dataclasses
import hashlib
from hmac import compare_digest
from os import abort
import secrets
import sqlite3
from termios import XCASE
import textwrap
import databases
from quart import Quart, g
from quart_schema import validate_request
from requests import request
from quart import abort, current_app
from functools import wraps
from secrets import compare_digest

app = Quart(__name__)


#  added all class regarding the user
@dataclasses.dataclass
class Wordlist:
    wordid: int
    screateWord: str

#  added all class regarding the user
class gameInfo:
    gameId: int
    userId: int
    wordId: int
    gamestat: bool
    user_attempts: int

#  added all class regarding the user
@dataclasses.dataclass
class userInfo:
    id: int
    user_name: str
    user_password: str
    # gameStatics: str

async def _get_db():
    db = getattr(g, "_sqlite_db", None)
    if db is None:
        db= g._sqlite_db = databases.Database('sqlite+aiosqlite:/wordle.db')
        await db.connect()
    return db


@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()


@app.route("/", methods=["GET"])
def index():
    return textwrap.dedent(
        """
        <h1>Distant Reading Archive</h1>
        <p>A prototype API for distant reading of science fiction novels.</p>\n
        """
    )


@app.route("/user/all", methods=["GET"])
async def all_user():
    db = await _get_db()
    all_books = await db.fetch_all("SELECT * FROM user;")

    return list(map(dict, all_books))




@app.route("/signup/", methods=["POST"])
@validate_request(userInfo)
async def usr_signup(data):
    db = await _get_db()
    person = dataclasses.asdict(data)
    try:
        id = await db.execute(
            """
            INSERT INTO user(id, user_name, user_password)
            VALUES(:id, :user_name, :user_password)
            """,
            person,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)
    
    person["id"] = id
    return person, 201

# http -a alex:cpsc449 http://127.0.0.1:5000/login

# @app.route("/login/", methods=['POST'])
# @validate_request(userInfo)
# async def auth(data):
#     db = await _get_db()
#     person = dataclasses.asdict(data)
#     try:
#         id = await db.execute()
#     except:
#         pass
#     password = login.password
#     if (name == "alex" and
#         compare_digest(password, "cpsc449")
#         ):
#         return {"authorization": True}
#     else:
#         return {"authorization": False}

# ALGORITHM = "pbkdf2_sha256"

# def hash_password(password, salt=None, iterations=260000):
#     if salt is None:
#         salt = secrets.token_hex(16)
#     assert salt and isinstance(salt, str) and "$" not in salt
#     assert isinstance(password, str)
#     pw_hash = hashlib.pbkdf2_hmac(
#         "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
#     )
#     b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
#     return "{}${}${}${}".format(ALGORITHM, iterations, salt, b64_hash)


# def verify_password(password, password_hash):
#     if (password_hash or "").count("$") != 3:
#         return False
#     algorithm, iterations, salt, b64_hash = password_hash.split("$", 3)
#     iterations = int(iterations)
#     assert algorithm == ALGORITHM
#     compare_hash = hash_password(password, salt, iterations)
#     return secrets.compare_digest(password_hash, compare_hash)























