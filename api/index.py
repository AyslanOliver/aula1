from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from database import init_db, create_user, authenticate_user, get_dashboard_stats, get_chart_data, create_route, get_routes, create_despesa, get_despesas

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

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!')
    return redirect(url_for('login'))

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
        user_id = session.get('user_id')
        
        if create_route(user_id, origem, destino, distancia, tempo_estimado):
            flash('Rota cadastrada com sucesso!', 'success')
        else:
            flash('Erro ao cadastrar rota!', 'error')
        return redirect(url_for('routes'))
    
    return render_template('routes.html')

@app.route('/view-routes')
def view_routes():
    user_id = session.get('user_id')
    routes = get_routes(user_id)
    return render_template('view-routes.html', routes=routes)

@app.route('/cadastrar-despesa', methods=['GET', 'POST'])
def cadastrar_despesa():
    if request.method == 'POST':
        descricao = request.form['descricao']
        valor = request.form['valor']
        categoria = request.form['categoria']
        data = request.form['data']
        user_id = session.get('user_id')
        
        if create_despesa(user_id, descricao, valor, categoria, data):
            flash('Despesa cadastrada com sucesso!', 'success')
        else:
            flash('Erro ao cadastrar despesa!', 'error')
        return redirect(url_for('cadastrar_despesa'))
    
    return render_template('cadastrar-despesa.html')

@app.route('/visualizar-despesas')
def visualizar_despesas():
    user_id = session.get('user_id')
    despesas = get_despesas(user_id)
    return render_template('visualizar-despesas.html', despesas=despesas)

@app.route('/relatorios-despesas')
def relatorios_despesas():
    user_id = session.get('user_id')
    chart_data = get_chart_data(user_id)
    return render_template('relatorios-despesas.html', chart_data=chart_data)

@app.route('/charts')
def charts():
    user_id = session.get('user_id')
    chart_data = get_chart_data(user_id)
    return render_template('charts.html', chart_data=chart_data)

@app.route('/tables')
def tables():
    user_id = session.get('user_id')
    stats = get_dashboard_stats(user_id)
    return render_template('tables.html', stats=stats)

# Handler para Vercel
if __name__ == '__main__':
    app.run(debug=True)