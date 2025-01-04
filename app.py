from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb
import bcrypt

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '06071998'
app.config['MYSQL_DB'] = 'apartamentos_db'

# Secret key for sessions
app.secret_key = 'secretkey'

mysql = MySQL(app)

@app.route('/')
def index():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="06071998", db="apartamentos_db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome, descricao, latitude, longitude FROM apartamentos")
    apartamentos = cursor.fetchall()
    conn.close()

    apartamentos_formatados = [
        {"nome": ap[0], "descricao": ap[1], "latitude": ap[2], "longitude": ap[3]} for ap in apartamentos
    ]

    return render_template('index.html', apartamentos=apartamentos_formatados)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    # Verificar se o usuário está logado
    if 'user_id' not in session or session['user_type'] != 'dono':
        return redirect(url_for('login'))  # Redireciona para o login se não estiver logado

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        user_id = session['user_id']  # Pega o user_id da sessão
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO apartamentos(nome, descricao, latitude, longitude, user_id) VALUES (%s, %s, %s, %s, %s)", 
                    (nome, descricao, latitude, longitude, user_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    
    return render_template('cadastro.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']

        # Hash a senha
        hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios(nome, email, senha, tipo) VALUES (%s, %s, %s, %s)", 
                    (nome, email, hashed_password, tipo))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, senha, tipo FROM usuarios WHERE email = %s", [email])
        user = cur.fetchone()

        if user and bcrypt.checkpw(senha.encode('utf-8'), user[1].encode('utf-8')):
            session['user_id'] = user[0]  # Armazena o user_id na sessão
            session['user_type'] = user[2]  # Armazena o tipo de usuário (dono ou cliente)
            return redirect(url_for('index'))
        else:
            return "Credenciais inválidas", 401
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove o user_id da sessão para deslogar o usuário
    session.pop('user_id', None)
    session.pop('user_type', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

