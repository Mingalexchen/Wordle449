import json
import dataclasses
from hmac import compare_digest
from os import abort
from pydoc import Helper
import sqlite3
import textwrap
import databases
from quart import Quart, g, jsonify,abort, request
from quart_schema import validate_request, RequestSchemaValidationError
from secrets import compare_digest


app = Quart(__name__)

#  added all class regarding the user
@dataclasses.dataclass
class UserInfo:
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

# Helper Functions

#  Connect to the Database
async def _get_db():
    db = getattr(g, "_sqlite_db", None)
    if db is None:
        db = g._sqlite_db = databases.Database("sqlite+aiosqlite:/wordle.db")
        await db.connect()
    return db

##################################################
#############---modify game helper---#############
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


###################################################################
###################################################################
#Function to check weather word is in both correct.json or in valid.json or not
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


###################################################################
###################################################################
# Function to restrict user attempt upto 6 and cannot hit single attempt multiple times.
# example: user cannot hit attempt_1 for more than 1 time
async def restrict_attempt(game_id, attempt):
    db = await _get_db()
    word = await db.fetch_one(
        "SELECT * FROM GameStats WHERE game_id= :game_id", values={"game_id": game_id}
    )
    if word[attempt]:
        return False
    else:
        return True


###################################################################
###################################################################
# function will compare gussed word by the user and correct word assosiated with that particular user
# and will return the state of every attempt by the user.
# if character is at correct place - mark that character as Green Color
# if character is not at correct place but present in word at ant position  - mark that character as Yellow Color
# if character is not present in correct word - mark that character as Grey Color 
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

###################################################################
###################################################################
# Funtion to store the Win result track of each game played by the user.
#  if Won this function will update DB and return False(false means cannot continue same game) 
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

##############################################

# APIs
@app.route("/", methods=["GET"])
def index():
    return textwrap.dedent(
        """
        <h1>Welcome to wordle Game</h1>
        <p>Register if you are new.</p>\n
        <p>Register if you are new or login Through HTTP Request from Terminal.<p>
        """
    )

# to test below function (/signup) use below cmd
########################################################################################
# http POST http://127.0.0.1:5000/signup/ user_name=value1 user_password=value2

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
    person["user_id"] = f'Your User_id is {list(id)[0]}'
    if id:
        return jsonify({"user_id":person["user_id"],"user_name":person["user_name"]}), 201
    else:
        abort(404)

#############################################################################
#############################################################################
# Login Function to authenticate user
# http POST http://127.0.0.1:5000/login user_name=value1 user_password=value2
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
            return jsonify({"authorization": True}), 200
        else:
            return jsonify({"authorization": "Failed-Incorrect Password"}), 401
    else:
        abort(404)

###########################################################
###########################################################
# User can start new game anytime and any number of times.
# http POST http://127.0.0.1:5000/<user_id>/newgame
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

        game_id = (await db.fetch_all(
        "SELECT game_id FROM GameStats WHERE user_id = :user_id",
        values={"user_id": user_id}))[-1][0]

    except sqlite3.IntegrityError as e:
        abort(409, e)
    return jsonify({"New Game Started": "success", "game_id": f'Your new game id is {game_id}'})

#############---game update---#############
# Function will accept game_id guess_word and attempt_number from user and store that guess word in DB
# return the result of that status of gussed word (green, yellow, grey) along with remaining attempts.
# $ http PUT http://127.0.0.1:5000/<game_id>/guessword entry=<valid_Word> attempt_number=<Attempt_Number>
@app.route("/<int:game_id>/guessword", methods=["PUT"])
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
                return jsonify({"1st attempt": "won", "word": word[0]})
            else:
                return {"1st attempt": "5 Attempts Remaining", "word": word[0]}
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
                return jsonify({"2nd attempt": "won", "word": word[0]})
            else:
                return jsonify({"2nd attempt": "4 Attempts Remaining", "word": word[0]})
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
                return jsonify({"3rd attempt": "won", "word": word[0]})
            else:
                return jsonify({"3rd attempt": "3 Attempts Remaining", "word": word[0]})
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
                return jsonify({"4th attempt": "won", "word": word[0]})
            else:
                return jsonify({"4th attempt": "2 Attempts Remaining", "word": word[0]})
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
                return jsonify({"5th attempt": "won", "word": word[0]})
            else:
                return jsonify({"5th attempt": "1 Attempts Remaining", "word": word[0]})
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
                return jsonify({"6th attempt": "won", "word": word[0]})
            else:
                return jsonify({"6th attempt": "you lost....!!! Start New Game", "word": word[0]})
        else:
            return {"attempt": "failed"}
    else:
        return {"attempt": "Not a valid word"}

#############---DB content helpers---#############
# http GET http://127.0.0.1:5000/games/info/<int:game_id>
@app.route("/games/info/<int:game_id>", methods=["GET"])
async def all_games(game_id):
    db = await _get_db()
    data = await db.fetch_all(
        "SELECT * FROM GameStats where game_id = :game_id;",
        values={"game_id": game_id},
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

#############-- Games Played by the User---#############
# http GET http://127.0.0.1:5000/user/info/<int:user_id>
@app.route("/user/info/<int:user_id>", methods=["GET"])
async def all_User_gamesInfo(user_id):
    db = await _get_db()
    data = await db.fetch_all(
        "SELECT game_result FROM GameStats where user_id = :user_id;",
        values={"user_id": user_id} )
    info = list(map(dict,data))
    show = dict()
    for i in info:
        try:
            if i["game_result"] == 0:
                show["In_Progress"]+=1
            elif i["game_result"] == 1:
                show["Total_Win"]+=1
            else:
                show["Total_Lost"]+=1
        except:
            if i["game_result"] == 0:
                show["In_Progress"] = 1
            elif i["game_result"] == 1:
                show["Total_Win"] = 1
            else:
                show["Total_Lost"] = 1
    return jsonify(show)

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