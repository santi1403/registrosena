from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os
import certifi

app = Flask(__name__)

# Conexión directa con tu contraseña nueva
MONGO_URI = "mongodb+srv://santibautista720_db_user:aaRlvwfm0xrIml6P@taller-sena.qjey0k8.mongodb.net/gestion_universitaria?retryWrites=true&w=majority&appName=Taller-Sena"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
    db = client['gestion_universitaria']
    coleccion = db['estudiantes']
    client.server_info()
    conexion_error = None
except Exception as e:
    conexion_error = str(e)

@app.route('/')
def index():
    if conexion_error:
        return render_template('error.html', error=conexion_error)
    try:
        estudiantes = list(coleccion.find({}))
        mensaje = request.args.get('mensaje', '')
        return render_template('index.html', estudiantes=estudiantes, mensaje=mensaje)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        doc = request.form['documento'].strip()
        nom = request.form['nombre'].strip()
        corr = request.form['correo'].strip()
        prog = request.form['programa'].strip()
        fich = request.form['ficha'].strip()
        score = request.form['puntuacion'].strip()

        if not all([doc, nom, corr, prog, fich, score]):
            return redirect(url_for('index', mensaje="Campos incompletos"))

        coleccion.insert_one({
            "documento": doc, "nombre": nom, "correo": corr,
            "programa": prog, "ficha": fich, "puntuacion": int(score)
        })
        return redirect(url_for('index', mensaje="Guardado exitosamente"))
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
