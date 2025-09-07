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
        # Verifica se MONGODB_URI está configurado
        if not MONGO_URI or MONGO_URI == 'mongodb://localhost:27017/':
            print("Warning: MONGODB_URI not configured properly")
            return False
            
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        
        # Test connection
        client.server_info()
        
        # Create indexes for better performance
        try:
            db.users.create_index("email", unique=True)
            db.routes.create_index("user_id")
            db.despesas.create_index("user_id")
        except Exception:
            pass  # Indexes may already exist
        
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

def create_route(user_id, origem, destino, distancia, tempo_estimado):
    """Cria uma nova rota"""
    try:
        client, db = get_db_connection()
        if not db:
            return False
        
        route_doc = {
            "user_id": user_id,
            "origem": origem,
            "destino": destino,
            "distancia": float(distancia) if distancia else 0,
            "tempo_estimado": tempo_estimado,
            "created_at": datetime.now()
        }
        
        result = db.routes.insert_one(route_doc)
        client.close()
        return bool(result.inserted_id)
    except Exception as e:
        print(f"Error creating route: {e}")
        return False

def get_routes(user_id=None):
    """Retorna lista de rotas"""
    try:
        client, db = get_db_connection()
        if not db:
            return []
        
        filter_query = {"user_id": user_id} if user_id else {}
        routes = list(db.routes.find(filter_query).sort("created_at", -1))
        
        # Convert ObjectId to string
        for route in routes:
            route["_id"] = str(route["_id"])
        
        client.close()
        return routes
    except Exception as e:
        print(f"Error getting routes: {e}")
        return []

def create_despesa(user_id, descricao, valor, categoria, data):
    """Cria uma nova despesa"""
    try:
        client, db = get_db_connection()
        if not db:
            return False
        
        despesa_doc = {
            "user_id": user_id,
            "descricao": descricao,
            "valor": float(valor),
            "categoria": categoria,
            "data": datetime.strptime(data, "%Y-%m-%d") if isinstance(data, str) else data,
            "created_at": datetime.now()
        }
        
        result = db.despesas.insert_one(despesa_doc)
        client.close()
        return bool(result.inserted_id)
    except Exception as e:
        print(f"Error creating despesa: {e}")
        return False

def get_despesas(user_id=None):
    """Retorna lista de despesas"""
    try:
        client, db = get_db_connection()
        if not db:
            return []
        
        filter_query = {"user_id": user_id} if user_id else {}
        despesas = list(db.despesas.find(filter_query).sort("data", -1))
        
        # Convert ObjectId to string and format dates
        for despesa in despesas:
            despesa["_id"] = str(despesa["_id"])
            if isinstance(despesa.get("data"), datetime):
                despesa["data"] = despesa["data"].strftime("%Y-%m-%d")
        
        client.close()
        return despesas
    except Exception as e:
        print(f"Error getting despesas: {e}")
        return []

# Banco de dados será inicializado quando necessário
# init_db() será chamado no index.py