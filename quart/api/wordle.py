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
from quart import abort, current_app, request
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
    user_name: str
    user_password: str

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
    all_books = await db.fetch_all("SELECT * FROM UserInfo;")

    return list(map(dict, all_books))


# to test below function (/signup) use below cmd
# curl -d '{"user_name":"value1", "user_password":"value2"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/signup/

@app.route("/signup/", methods=["POST"])
@validate_request(userInfo)
async def usr_signup(data):
    db = await _get_db()
    person = dataclasses.asdict(data)
    try:
        id = await db.execute(
            """
            INSERT INTO UserInfo(user_name, user_password)
            VALUES(:user_name, :user_password)
            """,
            person,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)
    
    person["user_name"] = id
    return person, 201





# to test below function (/login) use below cmd
# curl -d '{"user_name":"user1", "user_password":"abc123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/login

@app.route("/login", methods=["POST"])
@validate_request(userInfo)
async def auth(data):
    
    db = await _get_db()
    person = dataclasses.asdict(data)
    userinfo = await db.fetch_one("SELECT * FROM UserInfo WHERE user_name = :user_name", values={"user_name": person['user_name']})
    app.logger.debug(userinfo)
    if userinfo:
        login_info = dict(userinfo)
        if (person['user_name'] == login_info["user_name"] and
            compare_digest(person['user_password'], login_info["user_password"])
            ):
            return {"authorization": True}
        else:
            abort(401)
    else:
        abort(404)

