from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb
import bcrypt
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurações de upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cria o diretório de upload, caso não exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se o arquivo possui uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    # Conexão com o banco
    conn = MySQLdb.connect(host="localhost", user="root", passwd="06071998", db="apartamentos_db")
    cursor = conn.cursor()

    # Obtém os parâmetros do filtro
    preco = request.args.get('preco', '')
    localizacao = request.args.get('localizacao', '')
    tipo = request.args.get('tipo', '')

    # Criação da query SQL com as condições dinâmicas
    query = "SELECT id, nome, descricao, latitude, longitude, fotos, preco, tipo_imovel FROM apartamentos WHERE 1=1"
    params = []

    # Filtro de preço
    if preco == 'baixo':
        query += " AND preco < 500"
    elif preco == 'medio':
        query += " AND preco BETWEEN 500 AND 1000"
    elif preco == 'alto':
        query += " AND preco > 1000"

    # Filtro de localização
    if localizacao:
        query += " AND (bairro LIKE %s OR cidade LIKE %s)"
        params.extend([f"%{localizacao}%", f"%{localizacao}%"])

    # Filtro de tipo de imóvel
    if tipo:
        query += " AND tipo_imovel = %s"
        params.append(tipo)

    # Executa a consulta
    cursor.execute(query, params)
    apartamentos = cursor.fetchall()
    conn.close()

    # Formata os apartamentos com o id
    apartamentos_formatados = [
        {
            "id": ap[0],  # Inclui o id do apartamento
            "nome": ap[1],
            "descricao": ap[2],
            "latitude": ap[3],
            "longitude": ap[4],
            "fotos": ap[5].split(',') if ap[5] else [],
            "preco": ap[6],
            "tipo": ap[7]
        } 
        for ap in apartamentos
    ]

    return render_template('index.html', apartamentos=apartamentos_formatados)

    # Conexão com o banco
    conn = MySQLdb.connect(host="localhost", user="root", passwd="06071998", db="apartamentos_db")
    cursor = conn.cursor()

    # Obtém os parâmetros do filtro
    preco = request.args.get('preco', '')
    localizacao = request.args.get('localizacao', '')
    tipo = request.args.get('tipo', '')

    # Criação da query SQL com as condições dinâmicas
    query = "SELECT nome, descricao, latitude, longitude, fotos, preco, tipo_imovel FROM apartamentos WHERE 1=1"
    params = []

    # Filtro de preço
    if preco == 'baixo':
        query += " AND preco < 500"
    elif preco == 'medio':
        query += " AND preco BETWEEN 500 AND 1000"
    elif preco == 'alto':
        query += " AND preco > 1000"

    # Filtro de localização
    if localizacao:
        query += " AND (bairro LIKE %s OR cidade LIKE %s)"
        params.extend([f"%{localizacao}%", f"%{localizacao}%"])

    # Filtro de tipo de imóvel
    if tipo:
        query += " AND tipo_imovel = %s"
        params.append(tipo)

    # Executa a consulta
    cursor.execute(query, params)
    apartamentos = cursor.fetchall()
    conn.close()

    # Formata os apartamentos
    apartamentos_formatados = [
        {
            "nome": ap[0],
            "descricao": ap[1],
            "latitude": ap[2],
            "longitude": ap[3],
            "fotos": ap[4].split(',') if ap[4] else [],
            "preco": ap[5],
            "tipo": ap[6]
        } 
        for ap in apartamentos
    ]

    return render_template('index.html', apartamentos=apartamentos_formatados)

@app.route('/upload', methods=['POST'])
def upload():
    # Verifica se o usuário está logado e é do tipo "dono"
    if 'user_id' not in session or session['user_type'] != 'dono':
        return "Usuário não autorizado", 403

    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400

    file = request.files['file']

    if file.filename == '':
        return "Nenhum arquivo selecionado", 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return {"file_path": file_path}, 200

    return "Arquivo não permitido", 400

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'user_id' not in session or session['user_type'] != 'dono':
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            nome = request.form['nome']
            descricao = request.form['descricao']
            latitude = request.form['latitude']
            longitude = request.form['longitude']
            file_paths = request.form.get('filePaths', '')  # Pega os caminhos das fotos ou vazio
            user_id = session['user_id']

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO apartamentos(nome, descricao, latitude, longitude, user_id, fotos) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, descricao, latitude, longitude, user_id, file_paths))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('index'))
        except Exception as e:
            return f"Erro ao processar o formulário: {e}", 400

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

@app.route('/apartamento/<int:id>', methods=['GET'])
def apartamento(id):
    conn = MySQLdb.connect(host="localhost", user="root", passwd="06071998", db="apartamentos_db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome, descricao, latitude, longitude, fotos, preco, tipo_imovel FROM apartamentos WHERE id = %s", [id])
    apartamento = cursor.fetchone()
    conn.close()

    if apartamento:
        apartamento_formatado = {
            "nome": apartamento[0],
            "descricao": apartamento[1],
            "latitude": apartamento[2],
            "longitude": apartamento[3],
            "fotos": apartamento[4].split(',') if apartamento[4] else [],
            "preco": apartamento[5],
            "tipo": apartamento[6],
            "id": id
        }
        return render_template('apartamento.html', apartamento=apartamento_formatado)
    else:
        return "Apartamento não encontrado", 404
    


@app.route('/meus_apartamentos', methods=['GET'])
def meus_apartamentos():
    # Verifica se o usuário está logado e é do tipo "dono"
    if 'user_id' not in session or session['user_type'] != 'dono':
        return redirect(url_for('login'))

    # Obtém o user_id da sessão
    user_id = session['user_id']

    # Conexão com o banco de dados
    conn = MySQLdb.connect(host="localhost", user="root", passwd="06071998", db="apartamentos_db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, descricao, latitude, longitude, fotos, preco, tipo_imovel FROM apartamentos WHERE user_id = %s", [user_id])
    apartamentos = cursor.fetchall()
    conn.close()

    # Formatação dos apartamentos
    apartamentos_formatados = [
        {
            "id": ap[0],
            "nome": ap[1],
            "descricao": ap[2],
            "latitude": ap[3],
            "longitude": ap[4],
            "fotos": ap[5].split(',') if ap[5] else [],
            "preco": ap[6],
            "tipo": ap[7]
        } 
        for ap in apartamentos
    ]

    return render_template('meus_apartamentos.html', apartamentos=apartamentos_formatados)


@app.route('/apartamento/editar/<int:id>', methods=['GET', 'POST'])
def editar_apartamento(id):
    # Verifica se o usuário está logado e é do tipo "dono"
    if 'user_id' not in session or session['user_type'] != 'dono':
        return redirect(url_for('login'))

    # Conexão com o banco de dados
    conn = MySQLdb.connect(host="localhost", user="root", passwd="06071998", db="apartamentos_db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome, descricao, latitude, longitude, fotos, preco, tipo_imovel FROM apartamentos WHERE id = %s", [id])
    apartamento = cursor.fetchone()
    conn.close()

    # Se o apartamento não existe, retorna erro
    if not apartamento:
        return "Apartamento não encontrado", 404

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        preco = request.form['preco']
        tipo_imovel = request.form['tipo_imovel']
        fotos = request.form['fotos']  # Imagens podem ser atualizadas ou mantidas

        # Atualiza as informações no banco de dados
        conn = MySQLdb.connect(host="localhost", user="root", passwd="06071998", db="apartamentos_db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE apartamentos 
            SET nome = %s, descricao = %s, latitude = %s, longitude = %s, preco = %s, tipo_imovel = %s, fotos = %s
            WHERE id = %s
        """, (nome, descricao, latitude, longitude, preco, tipo_imovel, fotos, id))
        conn.commit()
        conn.close()

        return redirect(url_for('apartamento', id=id))  # Redireciona para a página de detalhes do apartamento

    # Caso seja um GET, preenche o formulário com as informações atuais
    apartamento_formatado = {
        "id": id,
        "nome": apartamento[0],
        "descricao": apartamento[1],
        "latitude": apartamento[2],
        "longitude": apartamento[3],
        "fotos": apartamento[4],
        "preco": apartamento[5],
        "tipo_imovel": apartamento[6]
    }

    return render_template('editar_apartamento.html', apartamento=apartamento_formatado)




if __name__ == '__main__':
    app.run(debug=True)
