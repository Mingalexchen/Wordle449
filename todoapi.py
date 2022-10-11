from quart import Quart

app = Quart(__name__)

@app.route("/")
async def index() -> str:
    return " Able to return the data form the datbases"
