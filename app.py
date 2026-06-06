from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import re

app = Flask(__name__)

# --- CONEXIÓN A MONGO ---
MONGO_URI = "mongodb+srv://santibautista720_db_user:C603b1ip8J1SdKne@taller-sena.qjey0k8.mongodb.net/?appName=Taller-Sena"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    db = client['gestion_universitaria']
    coleccion = db['estudiantes']
    client.server_info()
    conexion_error = None
    print("[SUCCESS] NEON NEXUS CONNECTED")
except Exception as e:
    conexion_error = str(e)
    print(f"[ERROR] DATABASE OFFLINE: {e}")

@app.route('/')
def index():
    if conexion_error:
        return render_template('error.html', error=conexion_error)
    try:
        # Ranking por puntuación
        todos = list(coleccion.find({}).sort("puntuacion", -1))
        mensaje = request.args.get('mensaje', '')
        return render_template('index.html', estudiantes=todos, mensaje=mensaje)
    except Exception as e:
        return render_template('error.html', error=e)

@app.route('/registrar', methods=['POST'])
def registrar():
    if conexion_error:
        return render_template('error.html', error=conexion_error)
    try:
        doc = request.form['documento'].strip()
        nom = request.form['nombre'].strip()
        corr = request.form['correo'].strip()
        prog = request.form['programa'].strip()
        fich = request.form['ficha'].strip()
        score = request.form['puntuacion'].strip()

        # Validaciones de seguridad
        if not all([doc, nom, corr, prog, fich, score]):
            return redirect(url_for('index', mensaje="Error: Transmisión de datos incompleta."))
        
        if coleccion.find_one({"documento": doc}):
            return redirect(url_for('index', mensaje=f"Error: Sujeto {doc} ya existe en el núcleo."))

        coleccion.insert_one({
            "documento": doc, "nombre": nom, "correo": corr,
            "programa": prog, "ficha": fich, "puntuacion": int(score)
        })
        return redirect(url_for('index', mensaje="Sincronización exitosa con la Memoria Central."))
    except Exception as e:
        return render_template('error.html', error=e)

if __name__ == '__main__':
    app.run(debug=True)