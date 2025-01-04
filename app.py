from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '06071998'
app.config['MYSQL_DB'] = 'apartamentos_db'

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
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO apartamentos(nome, descricao, latitude, longitude) VALUES (%s, %s, %s, %s)", 
                    (nome, descricao, latitude, longitude))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)
