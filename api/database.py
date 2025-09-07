import sqlite3
import os
from datetime import datetime
import hashlib

# Caminho para o banco de dados
DB_PATH = '/tmp/database.db' if os.environ.get('VERCEL') else 'database.db'

def init_db():
    """Inicializa o banco de dados SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            birth_date TEXT,
            license_plate TEXT,
            car_model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            origem TEXT NOT NULL,
            destino TEXT NOT NULL,
            distancia REAL,
            tempo_estimado TEXT,
            route_date TEXT,
            route_name TEXT,
            vehicle_type TEXT,
            destination_city TEXT,
            total_packages INTEGER,
            loose_packages INTEGER,
            has_helper BOOLEAN,
            is_sunday_holiday BOOLEAN,
            total_value REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT NOT NULL,
            data TEXT NOT NULL,
            payment_method TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Retorna uma conexão com o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_user(email, password, name="", birth_date=None, license_plate=None, car_model=None):
    """Cria um novo usuário"""
    try:
        conn = get_db_connection()
        
        # Verifica se o usuário já existe
        existing_user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            conn.close()
            return {"success": False, "message": "Usuário já existe"}
        
        # Hash da senha
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn.execute('''
            INSERT INTO users (email, password, name, birth_date, license_plate, car_model)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, password_hash, name, birth_date, license_plate, car_model))
        
        conn.commit()
        user_id = conn.lastrowid
        conn.close()
        
        return {"success": True, "user_id": user_id}
    except Exception as e:
        return {"success": False, "message": str(e)}

def authenticate_user(email, password):
    """Autentica um usuário"""
    try:
        conn = get_db_connection()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = conn.execute('''
            SELECT id, email, name FROM users 
            WHERE email = ? AND password = ?
        ''', (email, password_hash)).fetchone()
        
        conn.close()
        
        if user:
            return {
                "success": True,
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "name": user['name']
                }
            }
        else:
            return {"success": False, "message": "Credenciais inválidas"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_dashboard_stats(user_id=None):
    """Retorna estatísticas para o dashboard"""
    try:
        conn = get_db_connection()
        
        # Total de rotas
        if user_id:
            total_routes = conn.execute('SELECT COUNT(*) FROM routes WHERE user_id = ?', (user_id,)).fetchone()[0]
            total_expenses = conn.execute('SELECT COUNT(*) FROM despesas WHERE user_id = ?', (user_id,)).fetchone()[0]
            total_value = conn.execute('SELECT SUM(valor) FROM despesas WHERE user_id = ?', (user_id,)).fetchone()[0] or 0
        else:
            total_routes = conn.execute('SELECT COUNT(*) FROM routes').fetchone()[0]
            total_expenses = conn.execute('SELECT COUNT(*) FROM despesas').fetchone()[0]
            total_value = conn.execute('SELECT SUM(valor) FROM despesas').fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_routes": total_routes,
            "total_expenses": total_expenses,
            "total_value": total_value,
            "active_users": 1
        }
    except Exception as e:
        return {
            "total_routes": 0,
            "total_expenses": 0,
            "total_value": 0,
            "active_users": 0
        }

def get_chart_data(user_id=None):
    """Retorna dados para gráficos"""
    try:
        conn = get_db_connection()
        
        # Despesas por categoria
        if user_id:
            expenses_by_category = conn.execute('''
                SELECT categoria, SUM(valor) as total 
                FROM despesas 
                WHERE user_id = ?
                GROUP BY categoria
            ''', (user_id,)).fetchall()
            
            monthly_expenses = conn.execute('''
                SELECT strftime('%Y-%m', data) as month, SUM(valor) as total 
                FROM despesas 
                WHERE user_id = ?
                GROUP BY strftime('%Y-%m', data)
                ORDER BY month
            ''', (user_id,)).fetchall()
        else:
            expenses_by_category = conn.execute('''
                SELECT categoria, SUM(valor) as total 
                FROM despesas 
                GROUP BY categoria
            ''').fetchall()
            
            monthly_expenses = conn.execute('''
                SELECT strftime('%Y-%m', data) as month, SUM(valor) as total 
                FROM despesas 
                GROUP BY strftime('%Y-%m', data)
                ORDER BY month
            ''').fetchall()
        
        conn.close()
        
        return {
            "expenses_by_category": [dict(row) for row in expenses_by_category],
            "monthly_expenses": [dict(row) for row in monthly_expenses]
        }
    except Exception as e:
        return {
            "expenses_by_category": [],
            "monthly_expenses": []
        }

# Inicializar banco de dados
init_db()