import base64
import dataclasses
import hashlib
import secrets
from termios import XCASE
import textwrap
import databases
from quart import Quart, g, jsonify
from requests import head, request


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
class userInfo:
    userId: int
    userName: str
    userPassword: str
    gameStatics: str

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
async def all_books():
    db = await _get_db()
    all_books = await db.fetch_all("SELECT * FROM user;")

    return list(map(dict, all_books))




@app.route("/user/signup/<user_name>", methods=["POST"])
async def usr_signup(user_name):
    try:
        data_header = request.headers.get("Authorization")
        data = base64.b64decode(data_header[8:]).decode("utf-8").split("$")
        if data is not None:
            return data
        else:
            return 'Failed!!!!!!!!!!!!!!!!'
        # data = request.get_json()
        # db = await _get_db()
        # c = db.cursor()
        # query = f'INSERT INTO USER VALUES ({data[0]},{data[1]},{data[2]})'
        # c.exeute(query)
        # db.commit()
        # return {"value Insertd":True} 
    except:
        return "Insert failed"

# @app.route("/user/login", methods=["Post"])
# async def all_books():
#     db = await _get_db()
#     all_books = await db.fetch_all("SELECT * FROM user;")

#     return list(map(dict, all_books))



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























