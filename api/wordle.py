# Science Fiction Novel API - Quart Edition
#
# Adapted from "Creating Web APIs with Python and Flask"
# <https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask>.
#

import collections
import dataclasses
import sqlite3
import textwrap

import databases
import toml

from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request
from secrets import compare_digest



app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

#############---DB schema---#############
@dataclasses.dataclass
class UserInfo:
    user_id: int
    user_name: str
    user_password: str
class GameStats:
    game_id: int
    user_id: int
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
#############################################


#############---DB connection---#############
async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database


def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db


@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()
#############################################


#############---main page---#############
@app.route("/", methods=["GET"])
def front_page():
    return textwrap.dedent(
        """
        <h1>welcoe to wordy</h1>
        <p>Register if you are new. \nAlready have an account? Login here.</p>\n
    """
    )
#############################################

#TBD
#@app.route("/register", methods=["POST"])



#############---login---#############
@app.route("/login")
async def auth():
    login = request.authorization
    name = login.username
    password = login.password
    if (name == "alex" and
        compare_digest(password, "cpsc449")
        ):
        return {"authorization": True}
    else:
        abort(401)
##############################################


#############---user games---#############
'''tbd
@app.route("user/games/info", methods=["GET"])
async def all_games():
    db = await _get_db()
    all_game = await db.fetch_all("SELECT * FROM GameStats;")

    return list(map(dict, all_game))
'''

##############################################




#############---DB content helpers---#############
@app.route("/games/info", methods=["GET"])
async def all_games():
    db = await _get_db()
    all_game = await db.fetch_all("SELECT * FROM GameStats;")

    return list(map(dict, all_game))

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



#############################################
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




'''
@app.route("/books/all", methods=["GET"])
async def all_books():
    db = await _get_db()
    all_books = await db.fetch_all("SELECT * FROM books;")

    return list(map(dict, all_books))


@app.route("/books/<int:id>", methods=["GET"])
async def one_book(id):
    db = await _get_db()
    book = await db.fetch_one("SELECT * FROM books WHERE id = :id", values={"id": id})
    if book:
        return dict(book)
    else:
        abort(404)





@app.route("/books/", methods=["POST"])
@validate_request(Book)
async def create_book(data):
    db = await _get_db()
    book = dataclasses.asdict(data)
    try:
        id = await db.execute(
            """
            INSERT INTO books(published, author, title, first_sentence)
            VALUES(:published, :author, :title, :first_sentence)
            """,
            book,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    book["id"] = id
    return book, 201, {"Location": f"/books/{id}"}


SearchParam = collections.namedtuple("SearchParam", ["name", "operator"])
SEARCH_PARAMS = [
    SearchParam(
        "author",
        "LIKE",
    ),
    SearchParam(
        "published",
        "=",
    ),
    SearchParam(
        "title",
        "LIKE",
    ),
    SearchParam(
        "first_sentence",
        "LIKE",
    ),
]


@app.route("/books/search", methods=["GET"])
async def search():
    query_parameters = request.args

    sql = "SELECT * FROM books"

    conditions = []
    values = {}

    for param in SEARCH_PARAMS:
        app.logger.debug(f"{param}=")
        if query_parameters.get(param.name):
            if param.operator == "=":
                conditions.append(f"{param.name} = :{param.name}")
                values[param.name] = query_parameters[param.name]
            else:
                conditions.append(f"{param.name} LIKE :{param.name}")
                values[param.name] = f"%{query_parameters[param.name]}%"

    if conditions:
        sql += " WHERE "
        sql += " AND ".join(conditions)

    app.logger.debug(sql)

    db = await _get_db()
    results = await db.fetch_all(sql, values)

    return list(map(dict, results))
'''