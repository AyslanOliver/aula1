import pymongo
import os
from datetime import datetime
import hashlib
from bson.objectid import ObjectId

# MongoDB connection
MONGO_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'aula1_db'

def init_db():
    """Inicializa o banco de dados MongoDB"""
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        # Create indexes for better performance
        db.users.create_index("email", unique=True)
        db.routes.create_index("user_id")
        db.despesas.create_index("user_id")
        
        client.close()
        return True
    except Exception as e:
        print(f"MongoDB initialization error: {e}")
        return False

def get_db_connection():
    """Retorna uma conexão com o banco de dados MongoDB"""
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        return client, db
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None, None

def create_user(email, password, name="", birth_date=None, license_plate=None, car_model=None):
    """Cria um novo usuário"""
    try:
        client, db = get_db_connection()
        if not db:
            return {"success": False, "message": "Erro de conexão com o banco"}
        
        # Verifica se o usuário já existe
        existing_user = db.users.find_one({"email": email})
        if existing_user:
            client.close()
            return {"success": False, "message": "Usuário já existe"}
        
        # Hash da senha
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user_doc = {
            "email": email,
            "password": password_hash,
            "name": name,
            "birth_date": birth_date,
            "license_plate": license_plate,
            "car_model": car_model,
            "created_at": datetime.now()
        }
        
        result = db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        client.close()
        
        return {"success": True, "user_id": user_id}
    except Exception as e:
        return {"success": False, "message": str(e)}

def authenticate_user(email, password):
    """Autentica um usuário"""
    try:
        client, db = get_db_connection()
        if not db:
            return {"success": False, "message": "Erro de conexão com o banco"}
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = db.users.find_one({
            "email": email,
            "password": password_hash
        })
        
        client.close()
        
        if user:
            return {
                "success": True,
                "user": {
                    "id": str(user['_id']),
                    "email": user['email'],
                    "name": user.get('name', '')
                }
            }
        else:
            return {"success": False, "message": "Credenciais inválidas"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_dashboard_stats(user_id=None):
    """Retorna estatísticas para o dashboard"""
    try:
        client, db = get_db_connection()
        if not db:
            return {
                "total_routes": 0,
                "total_expenses": 0,
                "total_value": 0,
                "active_users": 0
            }
        
        # Total de rotas
        if user_id:
            filter_query = {"user_id": user_id}
            total_routes = db.routes.count_documents(filter_query)
            total_expenses = db.despesas.count_documents(filter_query)
            
            # Total value using aggregation
            pipeline = [{"$match": filter_query}, {"$group": {"_id": None, "total": {"$sum": "$valor"}}}]
            result = list(db.despesas.aggregate(pipeline))
            total_value = result[0]["total"] if result else 0
        else:
            total_routes = db.routes.count_documents({})
            total_expenses = db.despesas.count_documents({})
            
            # Total value using aggregation
            pipeline = [{"$group": {"_id": None, "total": {"$sum": "$valor"}}}]
            result = list(db.despesas.aggregate(pipeline))
            total_value = result[0]["total"] if result else 0
        
        client.close()
        
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
        client, db = get_db_connection()
        if not db:
            return {
                "expenses_by_category": [],
                "monthly_expenses": []
            }
        
        # Despesas por categoria
        match_stage = {"$match": {"user_id": user_id}} if user_id else {"$match": {}}
        
        category_pipeline = [
            match_stage,
            {"$group": {"_id": "$categoria", "total": {"$sum": "$valor"}}}
        ]
        expenses_by_category = list(db.despesas.aggregate(category_pipeline))
        
        monthly_pipeline = [
            match_stage,
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m", "date": "$data"}},
                    "total": {"$sum": "$valor"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        monthly_expenses = list(db.despesas.aggregate(monthly_pipeline))
        
        client.close()
        
        return {
            "expenses_by_category": [{"categoria": item["_id"], "total": item["total"]} for item in expenses_by_category],
            "monthly_expenses": [{"month": item["_id"], "total": item["total"]} for item in monthly_expenses]
        }
    except Exception as e:
        return {
            "expenses_by_category": [],
            "monthly_expenses": []
        }

# Inicializar banco de dados
init_db()