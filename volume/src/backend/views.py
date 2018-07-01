from run import app

@app.route("/")
def index():
    return "flask-skp"
