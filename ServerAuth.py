import json
import random
import threading
import time

import flask
from flask import request, jsonify, Flask
import bcrypt


app = Flask(__name__)

codigoActual = ""

def generarCodigo():
    global codigoActual
    print("Generando codigo")
    while True:
        num = random.randint(0, 99999)
        if num / 10000 < 1:
            numStr = f"{num:05}"
            codigoActual = numStr
        else:
            codigoActual = str(num)
        time.sleep(15)


@app.route('/')
def index():
    return "Server Auth"

@app.route('/code', methods=['POST'])
def code():
    pet = request.get_json()
    dicc = {"contrasena" : pet.get("contrasena")}

    try:
        with open("contrasena.key", "rb") as f:
            contHash = f.read()
            if bcrypt.checkpw(dicc.get("contrasena").encode("utf-8"), contHash):
                return jsonify({"estado": True,"codigoUnico": codigoActual})
            else:
                return jsonify({"estado": False,"codigoUnico": None})
    except FileNotFoundError:
        pass

@app.route("/validar", methods=["POST"])
def validar():
    pet = request.get_json()
    dicc = {"codigoUnico": pet.get("codigoUnico")}
    if dicc.get("codigoUnico") == codigoActual:
        return jsonify({"estado": True})
    else:
        return jsonify({"estado": False})

@app.route("/validarcont", methods=["POST"])
def validarCont():
    pet = request.get_json()
    dicc = {"contrasena": pet.get("contrasena")}
    with open("contrasena.key", "rb") as f:
        if bcrypt.checkpw(dicc.get("contrasena").encode("utf-8"), f.read()):
            return jsonify({"estado": True})
        else:
            return jsonify({"estado": False})

if __name__ == "__main__":
    threading.Thread(target=generarCodigo).start()
    app.run(host="127.0.0.1", port=5002)