from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import json
import plotly
import plotly.graph_objs as go
from database import db_manager
import hashlib
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configuração Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

class User(UserMixin):
    def __init__(self, user_id, email, name=""):
        self.id = user_id
        self.email = email
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    user_data = db_manager.get_user_by_id(user_id)
    if user_data:
        return User(str(user_data['_id']), user_data['email'], user_data.get('name', ''))
    return None

# PWA Routes
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('exampleInputEmail')
        password = request.form.get('exampleInputPassword')
        
        if not email or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')
        
        # Autenticar usuário
        result = db_manager.authenticate_user(email, password)
        
        if result['success']:
            user = User(str(result['user']['_id']), result['user']['email'], result['user'].get('name', ''))
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['message'], 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('confirm_password')
        birth_date = request.form.get('birth_date')
        license_plate = request.form.get('license_plate')
        car_model = request.form.get('car_model')
        
        if not all([email, password, first_name, last_name, birth_date, license_plate, car_model]):
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('register.html')
        
        if password != repeat_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('register.html')
        
        # Criar usuário
        result = db_manager.create_user(email, password, f"{first_name} {last_name}", birth_date, license_plate, car_model)
        
        if result['success']:
            flash('Conta criada com sucesso! Agora você pode fazer login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result['message'], 'error')
    
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('exampleInputEmail')
        if not email:
            flash('Por favor, digite seu email.', 'error')
            return render_template('forgot-password.html')
        
        # Aqui você implementaria a lógica de reset de senha
        flash('Se o email existir, você receberá instruções para redefinir sua senha.', 'info')
        return redirect(url_for('login'))
    
    return render_template('forgot-password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Calcular métricas específicas do negócio
    user_id = current_user.id
    
    # Calcular ganhos por quinzena (últimos 15 dias)
    from datetime import datetime, timedelta
    quinze_dias_atras = datetime.now() - timedelta(days=15)
    routes = db_manager.get_user_routes(user_id)
    ganhos_quinzena = 0
    pacotes_rota = 0
    pacotes_avulso = 0
    quantidade_pacotes_total = 0
    
    if routes.get('success'):
        for route in routes['routes']:
            route_date = route.get('route_date')
            if isinstance(route_date, str):
                route_date = datetime.strptime(route_date, '%Y-%m-%d')
            if route_date >= quinze_dias_atras:
                ganhos_quinzena += route.get('total_value', 0)
            
            # Calcular todas as métricas em um único loop
            pacotes_rota += route.get('total_packages', 0)
            pacotes_avulso += route.get('loose_packages', 0)
            quantidade_pacotes_total += route.get('total_packages', 0) + route.get('loose_packages', 0)
    
    # Calcular total de despesas
    expenses = db_manager.get_user_expenses(user_id)
    total_despesas = sum(expense.get('amount', 0) for expense in expenses)
    
    # Formatar valores para exibição
    ganhos_quinzena_formatted = f"{ganhos_quinzena:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    total_despesas_formatted = f"{total_despesas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    return render_template('index.html', 
                         ganhos_quinzena=ganhos_quinzena_formatted,
                         pacotes_rota=pacotes_rota,
                         pacotes_avulso=pacotes_avulso,
                         quantidade_pacotes_total=quantidade_pacotes_total,
                         total_despesas=total_despesas_formatted)

@app.route('/charts')
@login_required
def charts():
    # Carregar dados dos gráficos
    chart_data = db_manager.get_chart_data()
    
    # Criar gráficos com Plotly
    area_chart = create_area_chart(chart_data)
    bar_chart = create_bar_chart(chart_data)
    pie_chart = create_pie_chart(chart_data)
    
    return render_template('charts.html', 
                         area_chart=area_chart, 
                         bar_chart=bar_chart, 
                         pie_chart=pie_chart)

@app.route('/tables')
@login_required
def tables():
    # Carregar dados das tabelas
    table_data = db_manager.get_table_data()
    return render_template('tables.html', table_data=table_data)

@app.route('/routes', methods=['GET', 'POST'])
@login_required
def routes():
    if request.method == 'POST':
        route_date = request.form.get('route_date')
        route_name = request.form.get('route_name')
        vehicle_type = request.form.get('vehicle_type')
        destination_city = request.form.get('destination_city')
        total_packages = int(request.form.get('total_packages', 0))
        loose_packages = int(request.form.get('loose_packages', 0))
        has_helper = 'has_helper' in request.form
        is_sunday_holiday = 'is_sunday_holiday' in request.form
        
        if not all([route_date, route_name, vehicle_type, destination_city]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('routes.html')
        
        # Calculate total value
        base_value = 330 if vehicle_type == 'passeio' else 350
        loose_packages_value = loose_packages * 2
        helper_fee = 40 if has_helper else 0
        sunday_holiday_fee = 40 if is_sunday_holiday else 0
        total_value = base_value + loose_packages_value + helper_fee + sunday_holiday_fee
        
        # Save route to database
        result = db_manager.create_route(
            user_id=current_user.id,
            route_date=route_date,
            route_name=route_name,
            vehicle_type=vehicle_type,
            destination_city=destination_city,
            total_packages=total_packages,
            loose_packages=loose_packages,
            has_helper=has_helper,
            is_sunday_holiday=is_sunday_holiday,
            total_value=total_value
        )
        
        if result['success']:
            flash(f'Rota {route_name} cadastrada com sucesso! Valor total: R$ {total_value},00', 'success')
            return redirect(url_for('routes'))
        else:
            flash(result['message'], 'error')
    
    return render_template('routes.html')

@app.route('/view-routes')
@login_required
def view_routes():
    """Página para visualizar todas as rotas do usuário"""
    result = db_manager.get_user_routes(current_user.id)
    
    if result['success']:
        routes = result['routes']
    else:
        routes = []
        flash(result['message'], 'error')
    
    return render_template('view-routes.html', routes=routes)

@app.route('/edit-route/<route_id>', methods=['POST'])
@login_required
def edit_route(route_id):
    """Edita uma rota existente"""
    route_date = request.form.get('route_date')
    route_name = request.form.get('route_name')
    vehicle_type = request.form.get('vehicle_type')
    destination_city = request.form.get('destination_city')
    total_packages = int(request.form.get('total_packages', 0))
    loose_packages = int(request.form.get('loose_packages', 0))
    has_helper = 'has_helper' in request.form
    is_sunday_holiday = 'is_sunday_holiday' in request.form
    
    if not all([route_date, route_name, vehicle_type, destination_city]):
        flash('Por favor, preencha todos os campos obrigatórios.', 'error')
        return redirect(url_for('view_routes'))
    
    # Calculate total value
    base_value = 330 if vehicle_type == 'passeio' else 350
    loose_packages_value = loose_packages * 2
    helper_fee = 40 if has_helper else 0
    sunday_holiday_fee = 40 if is_sunday_holiday else 0
    total_value = base_value + loose_packages_value + helper_fee + sunday_holiday_fee
    
    # Update route in database
    result = db_manager.update_route(
        route_id=route_id,
        user_id=current_user.id,
        route_date=route_date,
        route_name=route_name,
        vehicle_type=vehicle_type,
        destination_city=destination_city,
        total_packages=total_packages,
        loose_packages=loose_packages,
        has_helper=has_helper,
        is_sunday_holiday=is_sunday_holiday,
        total_value=total_value
    )
    
    if result['success']:
        flash(f'Rota {route_name} atualizada com sucesso! Novo valor: R$ {total_value},00', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('view_routes'))

@app.route('/delete-route/<route_id>', methods=['POST'])
@login_required
def delete_route(route_id):
    """Deleta uma rota"""
    result = db_manager.delete_route(route_id, current_user.id)
    
    if result['success']:
        flash('Rota deletada com sucesso!', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('view_routes'))

@app.route('/get-route/<route_id>')
@login_required
def get_route(route_id):
    """Retorna dados de uma rota específica para edição"""
    try:
        result = db_manager.get_route_by_id(route_id)
        if result['success']:
            route = result['route']
            if route['user_id'] == current_user.id:
                return jsonify(route)
            else:
                return jsonify({'error': 'Rota não encontrada ou não autorizada'}), 404
        else:
            return jsonify({'error': result['message']}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rotas para gerenciamento de despesas
@app.route('/cadastrar-despesa', methods=['GET', 'POST'])
@login_required
def cadastrar_despesa():
    """Página para cadastrar despesas"""
    if request.method == 'POST':
        expense_date = request.form.get('expense_date')
        description = request.form.get('description')
        category = request.form.get('category')
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes', '')
        
        if not all([expense_date, description, category, amount, payment_method]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('cadastrar-despesa.html')
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('O valor deve ser maior que zero.', 'error')
                return render_template('cadastrar-despesa.html')
        except ValueError:
            flash('Valor inválido.', 'error')
            return render_template('cadastrar-despesa.html')
        
        # Criar despesa
        result = db_manager.create_expense(
            current_user.id, expense_date, description, category, 
            amount, payment_method, notes
        )
        
        if result['success']:
            flash('Despesa cadastrada com sucesso!', 'success')
            return redirect(url_for('visualizar_despesas'))
        else:
            flash(result['message'], 'error')
    
    return render_template('cadastrar-despesa.html')

@app.route('/visualizar-despesas')
@login_required
def visualizar_despesas():
    """Página para visualizar todas as despesas"""
    expenses = db_manager.get_user_expenses(current_user.id)
    return render_template('visualizar-despesas.html', expenses=expenses)

@app.route('/edit-expense/<expense_id>', methods=['POST'])
@login_required
def edit_expense(expense_id):
    """Edita uma despesa existente"""
    expense_date = request.form.get('expense_date')
    description = request.form.get('description')
    category = request.form.get('category')
    amount = request.form.get('amount')
    payment_method = request.form.get('payment_method')
    notes = request.form.get('notes', '')
    
    if not all([expense_date, description, category, amount, payment_method]):
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'success': False, 'message': 'O valor deve ser maior que zero'})
    except ValueError:
        return jsonify({'success': False, 'message': 'Valor inválido'})
    
    result = db_manager.update_expense(
        expense_id, current_user.id, expense_date, description, 
        category, amount, payment_method, notes
    )
    
    return jsonify(result)

@app.route('/deletar-despesa/<expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    """Deleta uma despesa"""
    result = db_manager.delete_expense(expense_id, current_user.id)
    return jsonify(result)

@app.route('/get-expense/<expense_id>')
@login_required
def get_expense(expense_id):
    """Retorna dados de uma despesa específica para edição"""
    try:
        expense = db_manager.get_expense_by_id(expense_id)
        if expense and expense['user_id'] == current_user.id:
            expense['_id'] = str(expense['_id'])
            return jsonify(expense)
        else:
            return jsonify({'error': 'Despesa não encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        # Atualizar dados do perfil
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        license_plate = request.form.get('license_plate')
        car_model = request.form.get('car_model')
        
        result = db_manager.update_user_profile(current_user.id, {
            'name': name,
            'birth_date': birth_date,
            'license_plate': license_plate,
            'car_model': car_model
        })
        
        if result['success']:
            flash('Perfil atualizado com sucesso!', 'success')
        else:
            flash('Erro ao atualizar perfil.', 'error')
        
        return redirect(url_for('perfil'))
    
    # Buscar dados do usuário
    user_data = db_manager.get_user_by_id(current_user.id)
    
    # Buscar estatísticas
    stats = {
        'total_routes': db_manager.count_user_routes(current_user.id),
        'total_expenses': db_manager.count_user_expenses(current_user.id)
    }
    
    return render_template('perfil.html', user_data=user_data, stats=stats)

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('Por favor, preencha todos os campos.', 'error')
        return redirect(url_for('perfil'))
    
    if new_password != confirm_password:
        flash('As senhas não coincidem.', 'error')
        return redirect(url_for('perfil'))
    
    if len(new_password) < 6:
        flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
        return redirect(url_for('perfil'))
    
    # Verificar senha atual
    user_data = db_manager.get_user_by_id(current_user.id)
    if not check_password_hash(user_data['password'], current_password):
        flash('Senha atual incorreta.', 'error')
        return redirect(url_for('perfil'))
    
    # Atualizar senha
    result = db_manager.update_user_password(current_user.id, new_password)
    
    if result['success']:
        flash('Senha alterada com sucesso!', 'success')
    else:
        flash('Erro ao alterar senha.', 'error')
    
    return redirect(url_for('perfil'))

@app.route('/performance-periodo')
@login_required
def performance_periodo():
    return render_template('performance-periodo.html')

@app.route('/analise-rentabilidade')
@login_required
def analise_rentabilidade():
    return render_template('analise-rentabilidade.html')

@app.route('/backup-dados')
@login_required
def backup_dados():
    return render_template('backup-dados.html')

@app.route('/relatorios-despesas')
@login_required
def relatorios_despesas():
    """Página de relatórios de despesas"""
    # Dados por categoria
    category_data = db_manager.get_expenses_by_category(current_user.id)
    
    # Dados mensais
    monthly_data = db_manager.get_monthly_expenses(current_user.id)
    
    # Buscar todas as despesas para calcular estatísticas
    all_expenses = db_manager.get_user_expenses(current_user.id)
    
    # Calcular estatísticas
    total_expenses = sum(expense.get('amount', 0) for expense in all_expenses)
    total_transactions = len(all_expenses)
    
    # Calcular média mensal (assumindo 12 meses)
    monthly_average = total_expenses / 12 if total_expenses > 0 else 0
    
    # Calcular ganhos totais das rotas
    routes = db_manager.get_user_routes(current_user.id)
    total_ganhos = 0
    if routes['success'] and routes['routes']:
        for route in routes['routes']:
            total_ganhos += route.get('total_value', 0)
    
    # Calcular lucro líquido (ganhos - despesas)
    lucro_liquido = total_ganhos - total_expenses
    
    # Criar gráficos
    category_chart = create_expense_category_chart(category_data)
    monthly_chart = create_expense_monthly_chart(monthly_data)
    
    return render_template('relatorios-despesas.html', 
                         category_chart=category_chart,
                         monthly_chart=monthly_chart,
                         category_data=category_data,
                         monthly_data=monthly_data,
                         total_expenses=total_expenses,
                         monthly_average=monthly_average,
                         total_transactions=total_transactions,
                         lucro_liquido=lucro_liquido,
                         total_ganhos=total_ganhos)


def create_area_chart(data):
    """Cria gráfico de área"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['area_chart']['labels'],
        y=data['area_chart']['values'],
        fill='tonexty',
        mode='lines',
        name='Earnings'
    ))
    fig.update_layout(
        title='Earnings Overview',
        xaxis_title='Month',
        yaxis_title='Earnings ($)',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_bar_chart(data):
    """Cria gráfico de barras"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data['bar_chart']['labels'],
        y=data['bar_chart']['values'],
        name='Revenue'
    ))
    fig.update_layout(
        title='Revenue Sources',
        xaxis_title='Source',
        yaxis_title='Revenue ($)',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_pie_chart(data):
    """Cria gráfico de pizza"""
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=data['pie_chart']['labels'],
        values=data['pie_chart']['values'],
        name='Revenue Distribution'
    ))
    fig.update_layout(
        title='Revenue Distribution',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_expense_category_chart(data):
    """Cria gráfico de pizza para despesas por categoria"""
    if not data:
        # Dados padrão se não houver despesas
        labels = ['Sem dados']
        values = [1]
        colors = ['#e3e6f0']
    else:
        labels = [item['_id'] for item in data]
        values = [item['total'] for item in data]
        colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796', '#5a5c69']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.4,
        marker=dict(colors=colors[:len(labels)]),
        textinfo='label+percent',
        textposition='auto'
    )])
    
    fig.update_layout(
        title=dict(
            text="Despesas por Categoria",
            x=0.5,
            font=dict(size=16, color='#5a5c69')
        ),
        font=dict(size=12, color='#5a5c69'),
        margin=dict(l=10, r=10, t=50, b=10),
        height=350,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def create_expense_monthly_chart(data):
    """Cria gráfico de barras para despesas mensais"""
    if not data:
        # Dados padrão se não houver despesas
        months = ['Sem dados']
        values = [0]
    else:
        months = [item['_id'] for item in data]
        values = [item['total'] for item in data]
    
    fig = go.Figure(data=[go.Bar(
        x=months, 
        y=values,
        marker=dict(
            color='#4e73df',
            line=dict(color='#2e59d9', width=1)
        ),
        text=[f'R$ {v:.2f}' for v in values],
        textposition='auto'
    )])
    
    fig.update_layout(
        title=dict(
            text="Despesas Mensais",
            x=0.5,
            font=dict(size=16, color='#5a5c69')
        ),
        xaxis=dict(
            title="Mês",
            titlefont=dict(size=14, color='#5a5c69'),
            tickfont=dict(size=12, color='#5a5c69'),
            gridcolor='#eaecf4'
        ),
        yaxis=dict(
            title="Valor (R$)",
            titlefont=dict(size=14, color='#5a5c69'),
            tickfont=dict(size=12, color='#5a5c69'),
            gridcolor='#eaecf4'
        ),
        font=dict(size=12, color='#5a5c69'),
        margin=dict(l=50, r=20, t=50, b=50),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/cadastrar-pacotes-assistentes', methods=['GET', 'POST'])
@login_required
def cadastrar_pacotes_assistentes():
    """Página para cadastrar pacotes para assistentes"""
    if request.method == 'POST':
        assistant_name = request.form.get('assistant_name')
        delivery_date = request.form.get('delivery_date')
        total_stops = int(request.form.get('total_stops', 0))
        packages_delivered = int(request.form.get('packages_delivered', 0))
        observations = request.form.get('observations', '')
        
        if not all([assistant_name, delivery_date, total_stops]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('cadastrar-pacotes-assistentes.html')
        
        if packages_delivered > total_stops:
            flash('O número de pacotes entregues não pode ser maior que o total de paradas.', 'error')
            return render_template('cadastrar-pacotes-assistentes.html')
        
        # Calcular valor total (R$ 2,00 por parada entregue)
        value_per_stop = 2.00
        total_value = packages_delivered * value_per_stop
        
        # Salvar no banco de dados
        result = db_manager.create_assistant_package(
            user_id=current_user.id,
            assistant_name=assistant_name,
            delivery_date=delivery_date,
            total_stops=total_stops,
            packages_delivered=packages_delivered,
            value_per_stop=value_per_stop,
            total_value=total_value,
            observations=observations
        )
        
        if result['success']:
            flash(f'Pacotes do assistente {assistant_name} cadastrados com sucesso! Valor total: R$ {total_value:.2f}', 'success')
            return redirect(url_for('cadastrar_pacotes_assistentes'))
        else:
            flash(result['message'], 'error')
    
    return render_template('cadastrar-pacotes-assistentes.html')

@app.route('/visualizar-pacotes-assistentes')
@login_required
def visualizar_pacotes_assistentes():
    """Página para visualizar todos os pacotes dos assistentes"""
    result = db_manager.get_user_assistant_packages(current_user.id)
    
    if result['success']:
        packages = result['packages']
        # Calcular totais
        total_value = sum(package.get('total_value', 0) for package in packages)
        total_packages = sum(package.get('packages_delivered', 0) for package in packages)
    else:
        packages = []
        total_value = 0
        total_packages = 0
        flash(result['message'], 'error')
    
    return render_template('visualizar-pacotes-assistentes.html', 
                         packages=packages, 
                         total_value=total_value,
                         total_packages=total_packages)

@app.route('/delete-assistant-package', methods=['POST'])
@login_required
def delete_assistant_package():
    try:
        data = request.get_json()
        package_id = data.get('package_id')
        
        if not package_id:
            return jsonify({'success': False, 'message': 'ID do pacote não fornecido'})
        
        success = db_manager.delete_assistant_package(current_user.id, package_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Pacote excluído com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao excluir pacote'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(
        debug=debug, 
        host='0.0.0.0', 
        port=port
    )