from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'clave_secreta_muy_segura'

# URLs de tu Gateway (FastAPI)
GATEWAY_URL = "http://localhost:8000"
# Token interno que definiste en el middleware del Gateway
INTERNAL_TOKEN = "tu_token_del_ini" 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        datos = {
            "nombre": request.form['nombre'],
            "email": request.form['email'],
            "password": request.form['password']
        }
        headers = {"X-Internal-Gateway-Token": INTERNAL_TOKEN}
        
        # Enviamos los datos al Gateway
        response = requests.post(f"{GATEWAY_URL}/register/", json=datos, headers=headers)
        res_json = response.json()
        
        if response.status_code == 201:
            flash(f"Registro exitoso. Tu carnet es: {res_json['data']['carnet']}", "success")
            return redirect(url_for('login'))
        else:
            flash(res_json.get('message', 'Error en el registro'), "danger")
            
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        datos = {
            "carnet": request.form['carnet'],
            "password": request.form['password']
        }
        headers = {"X-Internal-Gateway-Token": INTERNAL_TOKEN}
        
        response = requests.post(f"{GATEWAY_URL}/auth/login", json=datos, headers=headers)
        res_json = response.json()

        if response.status_code == 200:
            # Si el login es exitoso, pasamos los datos a la página de perfil
            user_data = res_json['data']['user']
            return render_template('perfil.html', user=user_data)
        else:
            flash(res_json.get('message', 'Carnet o contraseña incorrectos'), "danger")

    return render_template('login.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)