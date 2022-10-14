from quart import Quart, render_template

app = Quart(__name__)

@app.route("/")
async def show_form():
    return "from todo"
