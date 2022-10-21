from asyncio.log import logger
from distutils.log import debug
import json
import dataclasses
from hmac import compare_digest
from os import abort
import sqlite3
import textwrap
import databases
from quart import Quart, g, jsonify
import quart
from quart_schema import validate_request, RequestSchemaValidationError
from quart import abort, request
from secrets import compare_digest
import json

from sqlalchemy import false

app = Quart(__name__)

#  added all class regarding the user
@dataclasses.dataclass
class UserInfo:
    # user_id: int
    user_name: str
    user_password: str

class GameStats:
    game_id: int
    user_id: int
    game_result: int  # 0: in progress 1:win 2:lose
    answer_attempted: int  # number of attemped answers
    secret_word: str  # answer word
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
        db = g._sqlite_db = databases.Database("sqlite+aiosqlite:/wordle.db")
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
# http POST http://127.0.0.1:5100/signup/ user_name=value1 user_password=value2
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

    id = await db.fetch_one(
        "SELECT user_id FROM UserInfo WHERE user_name = :user_name",
        values={"user_name": person["user_name"]},
    )
    if id:
        return person, dict(id), 201
    else:
        abort(404)

# to test below function (/login) use below cmd
# curl -d '{"user_name":"user1", "user_password":"abc123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/login
# http POST http://127.0.0.1:5100/login user_name=value1 user_password=value2
@app.route("/login", methods=["POST"])
@validate_request(UserInfo)
async def auth(data):
    db = await _get_db()
    person = dataclasses.asdict(data)
    userinfo = await db.fetch_one(
        "SELECT * FROM UserInfo WHERE user_name = :user_name",
        values={"user_name": person["user_name"]},
    )
    # app.logger.debug(userinfo)
    if userinfo:
        login_info = dict(userinfo)
        if person["user_name"] == login_info["user_name"] and compare_digest(
            person["user_password"], login_info["user_password"]
        ):
            return {"authorization": True}
        else:
            return {"authorization": "Failed-Incorrect Password"}, 401
    else:
        abort(404)

#############---user games---#############
# ---returns all games played by the user
@app.route("/<int:id>/games", methods=["GET"])
async def user_games(id):
    db = await _get_db()
    all_game = await db.fetch_all(
        "SELECT * FROM GameStats WHERE user_id = :id;", values={"id": id}
    )
    if all_game:
        return list(map(dict, all_game))
    else:
        abort(404)

# tbd: user who have not played any game

##############################################

#############---compare string function---#############
# --- compare two 5 char words  answer  and  attempt
# --- and returns a json in formate {str1,str2,str3,str4,str5}
# --- where stri = "correct" if attempt[i] = answer[i]
# ---           = "almost there"  if attempt[i] != answer[i]
# ---                                && attempt[i] exist in answer
# ---           = "incorrect" if word[i] not exist in answer
async def compare_answer_str(attempt, answer):
    result_dict = {0: "error", 1: "error", 2: "error", 3: "error", 4: "error"}
    for i in range(5):
        if attempt[i] == answer[i]:
            result_dict[i] = "correct"
        elif attempt[i] in answer:
            result_dict[i] = "valid"
        else:
            result_dict[i] = "incorrect"

    result_json = json.dumps(result_dict)
    return result_json

#############---check range function---#############
# --- a function that returns game_result in GameStats
async def get_game_result(game_id):
    db = await _get_db()
    game_result = await db.fetch_one(
        "SELECT game_result FROM GameStats WHERE game_id = :id;", values={"id": game_id}
    )
    return game_result

#############---check attempted function---#############
# --- a function that returns answer_attempted in GameStats
async def get_attempt_number(game_id):
    db = await _get_db()
    answer_attempts = await db.fetch_one(
        "SELECT answer_attempted FROM GameStats WHERE game_id = :id;",
        values={"id": game_id},
    )
    return answer_attempts

#############---insert attempt function---#############
# --- a function that insert user entry to GameStats attempt_i
async def enter_answer(game_id, user_entry, attempt_number):
    db = await _get_db()
    if attempt_number == 0:
        insert_content = {"attempt_1": user_entry, "game_id": game_id}
        insert_content = dict(insert_content)
        try:
            await db.execute(
                """
            UPDATE GameStats 
            SET attempt_1 = :attempt_1
            WHERE game_id = :game_id;
            """,
                insert_content,
            )
        except sqlite3.IntegrityError as e:
            abort(409, e)
        return {"1st attempt": "finished"}
    elif attempt_number == 1:
        insert_content = {"attempt_2": user_entry, "game_id": game_id}
        insert_content = dict(insert_content)
        try:
            await db.execute(
                """
            UPDATE GameStats 
            SET attempt_2 = :attempt_2
            WHERE game_id = :game_id;
            """,
                insert_content,
            )
        except sqlite3.IntegrityError as e:
            abort(409, e)
        return {"2nd attempt": "finished"}
    elif attempt_number == 2:
        insert_content = {"attempt_3": user_entry, "game_id": game_id}
        insert_content = dict(insert_content)
        try:
            await db.execute(
                """
            UPDATE GameStats 
            SET attempt_3 = :attempt_3
            WHERE game_id = :game_id;
            """,
                insert_content,
            )
        except sqlite3.IntegrityError as e:
            abort(409, e)
        return {"3rd attempt": "finished"}
    elif attempt_number == 3:
        insert_content = {"attempt_4": user_entry, "game_id": game_id}
        insert_content = dict(insert_content)
        try:
            await db.execute(
                """
            UPDATE GameStats 
            SET attempt_4 = :attempt_4
            WHERE game_id = :game_id;
            """,
                insert_content,
            )
        except sqlite3.IntegrityError as e:
            abort(409, e)
        return {"4th attempt": "finished"}
    elif attempt_number == 4:
        insert_content = {"attempt_5": user_entry, "game_id": game_id}
        insert_content = dict(insert_content)
        try:
            await db.execute(
                """
            UPDATE GameStats 
            SET attempt_5 = :attempt_5
            WHERE game_id = :game_id;
            """,
                insert_content,
            )
        except sqlite3.IntegrityError as e:
            abort(409, e)
        return {"5th attempt": "finished"}
    elif attempt_number == 5:
        insert_content = {"attempt_6": user_entry, "game_id": game_id}
        insert_content = dict(insert_content)
        try:
            await db.execute(
                """
            UPDATE GameStats 
            SET attempt_6 = :attempt_6
            WHERE game_id = :game_id;
            """,
                insert_content,
            )
        except sqlite3.IntegrityError as e:
            abort(409, e)
        return {"6th attempt": "finished"}
    else:
        return {"attempt": "failed"}

#########---update answer_attempted function---#########
# --- a function that increases answer_attempted by 1
async def increase_attempt_number(game_id):
    db = await _get_db()
    game_id_dict = {"game_id": game_id}
    try:
        await db.execute(
            """
        UPDATE GameStats SET answer_attempted = answer_attempted + 1
        WHERE game_id = :game_id;
        """,
            game_id_dict,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)
    return {"attempt number": "updated"}

#############---respond to answer---#############
@app.route("/user/games/<int:game_id>", methods=["POST"])
async def respond_to_an_entry(game_id):
    if get_game_result(game_id) != 0:  # check if game has ended
        abort(400)  # return {"Attempt failed":"Game already ended!"}
    data = await request.get_json()  # receive user entry attempt
    if not data:  # check if received data
        abort(404)
    attempt = f"{data['attempt']}"  # convert user entry to string
    if attempt.len() != 5:  # if attempt not a length 5 word, return error
        abort(409)
    db = await _get_db()  # connect to DB
    attempt_number = get_attempt_number(game_id)
    if attempt_number > 5:  # check if the user have less than 6 answers
        abort(400)
    secret_word = await db.fetch_one(
        "SELECT secret_word FROM GameStats WHERE game_id = :id;", values={"id": game_id}
    )
    if not secret_word:  # if get secret_word fail return 400
        abort(400)
    answer = f"{secret_word}"
    return_json = await compare_answer_str(
        attempt, answer
    )  # compare user entry with secret word
    enter_answer(game_id, attempt, attempt_number)
    increase_attempt_number(game_id)
    return return_json

#############---DB content helpers---#############
# http POST http://127.0.0.1:5100/games/info game_id=<game_id>
@app.route("/games/info", methods=["POST"])
async def all_games():
    d = await request.get_json()
    db = await _get_db()
    data = await db.fetch_all(
        "SELECT * FROM GameStats where game_id = :game_id;",
        values={"game_id": d["game_id"]},
    )
    info = list(map(dict, data))
    del info[0]["answer_attempted"]
    del info[0]["game_id"]
    del info[0]["game_result"]
    del info[0]["secret_word"]
    del info[0]["user_id"]
    show = dict()
    if data[0]["game_result"] == 0:
        for i in info[0].values():
            if i is not None:
                show[i] = await matching_word(i, data[0]["game_id"])

        show["Message"] = f'You have {data[0]["answer_attempted"]} attempts left'
    elif data[0]["game_result"] == 1:
        show["Message"] = f'You Won the game!!!'
    else:
        show["Message"] = f'You Lost the game!!!'

    return jsonify(show)

@app.route("/user/info", methods=["GET"])
async def all_users():
    db = await _get_db()
    all_user = await db.fetch_all("SELECT * FROM UserInfo;")

    return list(map(dict, all_user))

@app.route("/word/info", methods=["GET"])
async def all_words():
    db = await _get_db()
    all_word = await db.fetch_all("SELECT * FROM SecretWords;")

    return list(map(dict, all_word))

##############################################

#############---new game---#############
# http POST http://127.0.0.1:5100/1/newgame
@app.route("/<int:user_id>/newgame", methods=["POST"])
async def new_game(user_id):
    db = await _get_db()
    new_secret_word = await db.fetch_one(
        "SELECT secret_word FROM SecretWords ORDER BY RANDOM() LIMIT 1;"
    )
    new_secret_word = new_secret_word[0]
    insert_content = {
        "game_id": None,
        "user_id": user_id,
        "game_result": 0,
        "answer_attempted": 6,
        "secret_word": new_secret_word,
        "attempt_1": None,
        "attempt_2": None,
        "attempt_3": None,
        "attempt_4": None,
        "attempt_5": None,
        "attempt_6": None,
    }
    insert_content = dict(insert_content)

    try:
        await db.execute(
            """
            INSERT INTO GameStats(game_id, user_id, game_result,
            answer_attempted, secret_word,
            attempt_1, attempt_2, attempt_3,
            attempt_4, attempt_5, attempt_6)
            VALUES(:game_id,:user_id, :game_result,
            :answer_attempted, :secret_word,
            :attempt_1, :attempt_2, :attempt_3,
            :attempt_4, :attempt_5, :attempt_6);
            """,
            insert_content,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)
    return {"New Game Started": "success"}

##################################################
#############---modify game helper---#############
@app.route("/<int:game_id>/increaseattempt", methods=["PUT"])
async def increase_attempt_val(game_id):
    db = await _get_db()
    game_id_dict = {"game_id": game_id}
    try:
        await db.execute(
            """
        UPDATE GameStats SET answer_attempted = answer_attempted - 1
        WHERE game_id = :game_id and answer_attempted >=0;
        """,
            game_id_dict,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)
    return {"update": "success"}


async def check_word(valid_word):
    db = await _get_db()
    word = await db.fetch_one(
        "SELECT * FROM ValidSecretWords WHERE valid_word = :valid_word",
        values={"valid_word": valid_word},
    )
    if word:
        return True
    else:
        return False


async def restrict_attempt(game_id, attempt):
    db = await _get_db()
    word = await db.fetch_one(
        "SELECT * FROM GameStats WHERE game_id= :game_id", values={"game_id": game_id}
    )
    if word[attempt]:
        return False
    else:
        return True


async def matching_word(valid_word, game_id):
    db = await _get_db()
    secret_word = (
        await db.fetch_one(
            "SELECT secret_word FROM GameStats WHERE game_id = :game_id",
            values={"game_id": game_id},
        )
    )[0]

    d = {}
    for i in range(len(valid_word)):
        if valid_word[i] == secret_word[i]:
            d[valid_word[i]] = (i, "Green")

    for i in range(len(valid_word)):
        for j in range(len(secret_word)):
            if valid_word[i] not in d.keys() and valid_word[i] in secret_word:
                d[valid_word[i]] = (i, "Yellow")

    for i in range(len(valid_word)):
        if valid_word[i] not in d.keys():
            d[valid_word[i]] = (i, "Grey")

    flag = False
    for i in d.values():
        if i[1] == "Yellow" or i[1] == "Grey":
            flag = True
            break
    return [d,flag]


async def check(tmp, game_id):
    app.logger.debug(tmp)
    for i in tmp[0].values():
        if i[1] == "Yellow" or i[1] == "Grey":
            return True

    db = await _get_db()
    try:
        await db.execute(
            """
                UPDATE GameStats SET game_result = 1
                WHERE game_id = :game_id;
                """,
            values={"game_id": game_id},
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    return False


#############---game update---#############
# $ http PUT http://127.0.0.1:5100/<game_id>/newmove entry=<valid_Word> attempt_number=<Attempt_Number>
@app.route("/<int:game_id>/newmove", methods=["PUT"])
async def update_game(game_id):
    db = await _get_db()
    data = await request.get_json()
    user_entry = f"{data['entry']}"
    attempt_number = int(f"{data['attempt_number']}")
    if await check_word(user_entry.lower()):
        tmp = {}
        if attempt_number == 1 and await restrict_attempt(game_id, "attempt_1"):

            insert_content = {"attempt_1": user_entry, "game_id": game_id}
            insert_content = dict(insert_content)
            try:
                attempt = await increase_attempt_val(game_id)
                await db.execute(
                    """
                UPDATE GameStats 
                SET attempt_1 = :attempt_1
                WHERE game_id = :game_id;
                """,
                    insert_content,
                )
            except sqlite3.IntegrityError as e:
                abort(409, e)
            word = tmp = await matching_word(user_entry, game_id)
            n = await check(tmp, game_id)
            if not n:
                return {"1st attempt": "won", "word": word}
            else:
                return {"1st attempt": "5 Attempts Remaining", "word": word}
        elif attempt_number == 2 and await restrict_attempt(game_id, "attempt_2"):

            insert_content = {"attempt_2": user_entry, "game_id": game_id}
            insert_content = dict(insert_content)
            try:
                attempt = await increase_attempt_val(game_id)
                await db.execute(
                    """
                UPDATE GameStats 
                SET attempt_2 = :attempt_2
                WHERE game_id = :game_id;
                """,
                    insert_content,
                )
            except sqlite3.IntegrityError as e:
                abort(409, e)
            word = tmp = await matching_word(user_entry, game_id)
            n = await check(tmp, game_id)
            if not n:
                return {"2nd attempt": "won", "word": word}
            else:
                return {"2nd attempt": "4 Attempts Remaining", "word": word}
        elif attempt_number == 3 and await restrict_attempt(game_id, "attempt_3"):

            insert_content = {"attempt_3": user_entry, "game_id": game_id}
            insert_content = dict(insert_content)
            try:
                attempt = await increase_attempt_val(game_id)
                await db.execute(
                    """
                UPDATE GameStats 
                SET attempt_3 = :attempt_3
                WHERE game_id = :game_id;
                """,
                    insert_content,
                )
            except sqlite3.IntegrityError as e:
                abort(409, e)
            word = tmp = await matching_word(user_entry, game_id)
            n = await check(tmp, game_id)
            if not n:
                return {"3rd attempt": "won", "word": word}
            else:
                return {"3rd attempt": "3 Attempts Remaining", "word": word}
        elif attempt_number == 4 and await restrict_attempt(game_id, "attempt_4"):
            insert_content = {"attempt_4": user_entry, "game_id": game_id}
            insert_content = dict(insert_content)
            try:
                attempt = await increase_attempt_val(game_id)
                await db.execute(
                    """
                UPDATE GameStats 
                SET attempt_4 = :attempt_4
                WHERE game_id = :game_id;
                """,
                    insert_content,
                )
            except sqlite3.IntegrityError as e:
                abort(409, e)
            word = tmp = await matching_word(user_entry, game_id)
            n = await check(tmp, game_id)
            if not n:
                return {"4th attempt": "won", "word": word}
            else:
                return {"4th attempt": "2 Attempts Remaining", "word": word}
        elif attempt_number == 5 and await restrict_attempt(game_id, "attempt_5"):
            insert_content = {"attempt_5": user_entry, "game_id": game_id}
            insert_content = dict(insert_content)
            try:
                attempt = await increase_attempt_val(game_id)
                await db.execute(
                    """
                UPDATE GameStats 
                SET attempt_5 = :attempt_5
                WHERE game_id = :game_id;
                """,
                    insert_content,
                )
            except sqlite3.IntegrityError as e:
                abort(409, e)
            word = tmp = await matching_word(user_entry, game_id)
            n = await check(tmp, game_id)
            if not n:
                return {"5th attempt": "won", "word": word}
            else:
                return {"5th attempt": "1 Attempts Remaining", "word": word}
        elif attempt_number == 6 and await restrict_attempt(game_id, "attempt_6"):
            insert_content = {"attempt_6": user_entry, "game_id": game_id}
            insert_content = dict(insert_content)
            try:
                attempt = await increase_attempt_val(game_id)
                await db.execute(
                    """
                UPDATE GameStats 
                SET attempt_6 = :attempt_6, game_result = 2
                WHERE game_id = :game_id;
                """,
                    insert_content,
                )
            except sqlite3.IntegrityError as e:
                abort(409, e)
            word = tmp = await matching_word(user_entry, game_id)
            n = await check(tmp, game_id)
            if not n:
                return {"6th attempt": "won", "word": word}
            else:
                return {"6th attempt": "you lost....!!! Start New Game", "word": word}
        else:
            return {"attempt": "failed"}
    else:
        return {"attempt": "Not a valid word"}


##############################################

#############---error handlers---#############
@app.errorhandler(404)
def not_found(e):
    return {"error": "The resource could not be found"}, 404


@app.errorhandler(RequestSchemaValidationError)
def bad_request(e):
    return {"error": str(e.validation_error)}, 400


@app.errorhandler(409)
def conflict(e):
    return {"error": str(e)}, 409


@app.errorhandler(401)
def conflict(e):
    return {"error": "Authorization failed!"}, 401


#############################################
