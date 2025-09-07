from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import sys

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, get_db_connection

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.secret_key = 'your-secret-key-here'

# Inicializar banco de dados
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Lógica de login aqui
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Lógica de registro aqui
        flash('Registro realizado com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

@app.route('/routes', methods=['GET', 'POST'])
def routes():
    if request.method == 'POST':
        origem = request.form['origem']
        destino = request.form['destino']
        distancia = request.form['distancia']
        tempo_estimado = request.form['tempo_estimado']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO routes (origem, destino, distancia, tempo_estimado) VALUES (?, ?, ?, ?)',
                    (origem, destino, distancia, tempo_estimado))
        conn.commit()
        conn.close()
        
        flash('Rota cadastrada com sucesso!', 'success')
        return redirect(url_for('routes'))
    
    return render_template('routes.html')

@app.route('/view-routes')
def view_routes():
    conn = get_db_connection()
    routes = conn.execute('SELECT * FROM routes ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('view-routes.html', routes=routes)

@app.route('/cadastrar-despesa', methods=['GET', 'POST'])
def cadastrar_despesa():
    if request.method == 'POST':
        descricao = request.form['descricao']
        valor = request.form['valor']
        categoria = request.form['categoria']
        data = request.form['data']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO despesas (descricao, valor, categoria, data) VALUES (?, ?, ?, ?)',
                    (descricao, valor, categoria, data))
        conn.commit()
        conn.close()
        
        flash('Despesa cadastrada com sucesso!', 'success')
        return redirect(url_for('cadastrar_despesa'))
    
    return render_template('cadastrar-despesa.html')

@app.route('/visualizar-despesas')
def visualizar_despesas():
    conn = get_db_connection()
    despesas = conn.execute('SELECT * FROM despesas ORDER BY data DESC').fetchall()
    conn.close()
    return render_template('visualizar-despesas.html', despesas=despesas)

@app.route('/relatorios-despesas')
def relatorios_despesas():
    conn = get_db_connection()
    despesas = conn.execute('SELECT * FROM despesas ORDER BY data DESC').fetchall()
    
    # Calcular totais por categoria
    totais = conn.execute('''
        SELECT categoria, SUM(valor) as total 
        FROM despesas 
        GROUP BY categoria
    ''').fetchall()
    
    conn.close()
    return render_template('relatorios-despesas.html', despesas=despesas, totais=totais)

@app.route('/charts')
def charts():
    conn = get_db_connection()
    # Dados para gráficos
    despesas_por_categoria = conn.execute('''
        SELECT categoria, SUM(valor) as total 
        FROM despesas 
        GROUP BY categoria
    ''').fetchall()
    
    despesas_por_mes = conn.execute('''
        SELECT strftime('%Y-%m', data) as mes, SUM(valor) as total 
        FROM despesas 
        GROUP BY strftime('%Y-%m', data)
        ORDER BY mes
    ''').fetchall()
    
    conn.close()
    return render_template('charts.html', 
                         despesas_por_categoria=despesas_por_categoria,
                         despesas_por_mes=despesas_por_mes)

@app.route('/tables')
def tables():
    conn = get_db_connection()
    despesas = conn.execute('SELECT * FROM despesas ORDER BY data DESC LIMIT 50').fetchall()
    routes = conn.execute('SELECT * FROM routes ORDER BY id DESC LIMIT 50').fetchall()
    conn.close()
    return render_template('tables.html', despesas=despesas, routes=routes)

# Handler para Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)

# Export para Vercel
app = app