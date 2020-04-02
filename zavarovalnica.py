## meni tole ne dela
from bottle import route, run

@route("/")
def zacetek():
    return "To je proba za local host"

run(host="localhost", port=8080)