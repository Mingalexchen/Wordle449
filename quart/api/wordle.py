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
from quart import Quart, g, jsonify
from quart_schema import validate_request
from quart import abort, current_app, request
from functools import wraps
from secrets import compare_digest
import json
import random

app = Quart(__name__)


#  added all class regarding the user
@dataclasses.dataclass
class UserInfo:
    user_name: str
    user_password: str
class GameStats:
    game_id: int
    user_name: str
    game_result: int   #0: in progress 1:win 2:lose
    answer_attempted: int   #number of attemped answers
    secret_word: str   #answer word
    attempt_1: str
    attempt_2: str
    attempt_3: str
    attempt_4: str
    attempt_5: str
    attempt_6: str
    
class SecretWords:
    secret_word: str

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

#  http wordle.local.gd:5100/user/all
@app.route("/user/all", methods=["GET"])
async def all_user():
    db = await _get_db()
    all_books = await db.fetch_all("SELECT * FROM UserInfo;")

    return list(map(dict, all_books))


# to test below function (/signup) use below cmd
# curl -d '{"user_name":"value1", "user_password":"value2"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/signup/

@app.route("/signup/", methods=["POST"])
@validate_request(UserInfo)
async def usr_signup(data):
    db = await _get_db()
    person = dataclasses.asdict(data)
    try:
        await db.execute(
            """
            INSERT INTO UserInfo(user_name, user_password)
            VALUES(:user_name, :user_password)
            """,
            person,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)
    
    return person, 201





# to test below function (/login) use below cmd
# curl -d '{"user_name":"user1", "user_password":"abc123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/login

@app.route("/login", methods=["POST"])
@validate_request(UserInfo)
async def auth(data):
    db = await _get_db()
    person = dataclasses.asdict(data)
    userinfo = await db.fetch_one("SELECT * FROM UserInfo WHERE user_name = :user_name", values={"user_name": person['user_name']})
    # app.logger.debug(userinfo)
    if userinfo:
        login_info = dict(userinfo)
        if (person['user_name'] == login_info["user_name"] and
            compare_digest(person['user_password'], login_info["user_password"])
            ):
            word_list = correct_json()
            word = random.choice(word_list)
            try:
                await db.execute(
                """
                INSERT INTO GameStats(user_name,answer_attempted, secret_word)
                VALUES(:user_name, :answer_attempted, :secret_word)
                """,
                values={"user_name":person['user_name'],"answer_attempted": 0,"secret_word": word }
                )
            except sqlite3.IntegrityError as e:
                abort(409, e)
            return {"authorization": True}
        else:
            return {"authorization": "Failed-Incorrect Password"},401
    else:
        abort(404)

##################################################

# curl -X GET "http://127.0.0.1:5100/startGame?user_name=value1"

# curl -d '{"user_name":"user1"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/startGame
@app.route("/startGame", methods=["POST"])
async def startGame():

    u_name = (await request.get_json())["user_name"]
    word_list = correct_json()
    word = random.choice(word_list)
    
    db = await _get_db()
   
    try:
        await db.execute(
            """
            INSERT INTO GameStats(user_name,answer_attempted, secret_word)
            VALUES(:user_name, :answer_attempted, :secret_word)
            """,
            values={"user_name":u_name,"answer_attempted": 0,"secret_word": word }
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)
   
    return jsonify({"authorization":200})
 
    
def correct_json():
    with open("correct.json", 'r') as f:
        data = json.load(f)
    return data




    
