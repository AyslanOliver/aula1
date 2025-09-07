from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from database import init_db, create_user, authenticate_user, get_dashboard_stats, get_chart_data

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize database
init_db()

@app.route('/')
def index():
    user_id = session.get('user_id')
    stats = get_dashboard_stats(user_id)
    return render_template('index.html', stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        result = authenticate_user(email, password)
        
        if result['success']:
            session['user_id'] = result['user']['id']
            session['user_email'] = result['user']['email']
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos!')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form.get('name', '')
        birth_date = request.form.get('birth_date')
        license_plate = request.form.get('license_plate')
        car_model = request.form.get('car_model')
        
        result = create_user(email, password, name, birth_date, license_plate, car_model)
        
        if result['success']:
            flash('Usuário criado com sucesso!')
            return redirect(url_for('login'))
        else:
            flash(result['message'])
    
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
    user_id = session.get('user_id')
    chart_data = get_chart_data(user_id)
    return render_template('charts.html', chart_data=chart_data)

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