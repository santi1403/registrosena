from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os
import certifi  # <- Fuerza a usar el almacén de certificados actualizado de certifi

app = Flask(__name__)

# --- CONFIGURACIÓN DE CONEXIÓN CON TU CONTRASEÑA ---
MONGO_URI = "mongodb+srv://santibautista720_db_user:aaRlvwfm0xrIml6P@taller-sena.qjey0k8.mongodb.net/gestion_universitaria?retryWrites=true&w=majority&appName=Taller-Sena"

try:
    # Le inyectamos tlsCAFile para que use los certificados de certifi instalados en Render
    client = MongoClient(
        MONGO_URI, 
        serverSelectionTimeoutMS=10000,
        tlsCAFile=certifi.where()  # <- SOLUCIÓN AL HANDSHAKE FALLIDO
    )
    db = client['gestion_universitaria']
    coleccion = db['estudiantes']
    
    # Validamos la conexión con el clúster
    client.server_info()
    conexion_error = None
    print("[SUCCESS] NEON NEXUS CONNECTED TO MONGODB ATLAS")
except Exception as e:
    conexion_error = str(e)
    print(f"[ERROR] DATABASE OFFLINE: {e}")

# ============================================================
# RUTAS DEL SISTEMA NEON NEXUS
# ============================================================

@app.route('/')
def index():
    if conexion_error:
        return render_template('error.html', error=conexion_error)
    try:
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

        if not all([doc, nom, corr, prog, fich, score]):
            return redirect(url_for('index', mensaje="Error: Transmisión de datos incompleta."))
        
        if coleccion.find_one({"documento": doc}):
            return redirect(url_for('index', mensaje=f"Error: El ID {doc} ya existe en el núcleo."))

        coleccion.insert_one({
            "documento": doc, 
            "nombre": nom, 
            "correo": corr,
            "programa": prog, 
            "ficha": fich, 
            "puntuacion": int(score)
        })
        return redirect(url_for('index', mensaje="Sincronización exitosa con la Memoria Central."))
    except Exception as e:
        return render_template('error.html', error=e)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
