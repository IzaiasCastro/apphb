from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    apartamentos = [
        {"nome": "Apartamento A", "descricao": "Apartamento próximo à praia", "latitude": -5.0917, "longitude": -42.8038},
        {"nome": "Apartamento B", "descricao": "Apartamento em bairro central", "latitude": -5.0850, "longitude": -42.8060},
        {"nome": "Apartamento C", "descricao": "Apartamento tranquilo", "latitude": -5.1010, "longitude": -42.8000},
        {"nome": "Apartamento D", "descricao": "Apartamento moderno", "latitude": -5.0950, "longitude": -42.8120}
    ]
    return render_template('index.html', apartamentos=apartamentos)

if __name__ == '__main__':
    app.run(debug=True)
