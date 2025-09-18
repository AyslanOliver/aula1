import pymongo
from pymongo import MongoClient
from datetime import datetime, date
import calendar
import hashlib

def get_current_fortnight():
    """Retorna as datas de início e fim da quinzena atual"""
    hoje = date.today()
    primeiro_dia = date(hoje.year, hoje.month, 1)
    ultimo_dia = date(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])
    
    # Primeira quinzena: 1-15
    if hoje.day <= 15:
        inicio = primeiro_dia
        fim = date(hoje.year, hoje.month, 15)
    # Segunda quinzena: 16-último dia do mês
    else:
        inicio = date(hoje.year, hoje.month, 16)
        fim = ultimo_dia
    
    return inicio, fim

def get_previous_fortnight():
    """Retorna as datas de início e fim da quinzena anterior"""
    hoje = date.today()
    
    # Se estamos na segunda quinzena (16-31)
    if hoje.day > 15:
        inicio = date(hoje.year, hoje.month, 1)
        fim = date(hoje.year, hoje.month, 15)
    # Se estamos na primeira quinzena (1-15)
    else:
        # Se for janeiro, volta para dezembro do ano anterior
        if hoje.month == 1:
            ano = hoje.year - 1
            mes = 12
        else:
            ano = hoje.year
            mes = hoje.month - 1
        
        inicio = date(ano, mes, 16)
        fim = date(ano, mes, calendar.monthrange(ano, mes)[1])
    
    return inicio, fim

class DatabaseManager:
    def __init__(self):
        # String de conexão MongoDB fornecida pelo usuário
        self.connection_string = "mongodb+srv://ayslano37:Walkingtonn1@demolicao.fk6aapp.mongodb.net/?retryWrites=true&w=majority&serverSelectionTimeoutMS=5000"
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Estabelece conexão com MongoDB"""
        try:
            # Configuração do cliente com timeout e retry
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=50,
                retryWrites=True
            )
            self.db = self.client['sb_admin_db']  # Nome do banco de dados
            # Testa a conexão
            self.client.admin.command('ping')
            print("Conexão com MongoDB estabelecida com sucesso!")
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(f"Erro de timeout ao conectar com MongoDB: {e}")
            print("Verifique sua conexão com a internet e as configurações de firewall")
        except pymongo.errors.ConnectionFailure as e:
            print(f"Falha na conexão com MongoDB: {e}")
            print("Verifique se o servidor MongoDB está acessível")
        except Exception as e:
            print(f"Erro ao conectar com MongoDB: {e}")
    
    def close_connection(self):
        """Fecha a conexão com MongoDB"""
        if self.client:
            self.client.close()
    
    # Métodos para autenticação de usuários
    def create_user(self, email, password, name="", birth_date=None, license_plate=None, car_model=None):
        """Cria um novo usuário"""
        try:
            users_collection = self.db['users']
            
            # Verifica se o usuário já existe
            if users_collection.find_one({"email": email}):
                return {"success": False, "message": "Usuário já existe"}
            
            # Hash da senha
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            user_data = {
                "email": email,
                "password": password_hash,
                "name": name,
                "birth_date": birth_date,
                "license_plate": license_plate,
                "car_model": car_model,
                "created_at": datetime.now(),
                "last_login": None
            }
            
            result = users_collection.insert_one(user_data)
            return {"success": True, "user_id": str(result.inserted_id)}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao criar usuário: {e}"}
    
    def authenticate_user(self, email, password):
        """Autentica um usuário"""
        try:
            users_collection = self.db['users']
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            user = users_collection.find_one({
                "email": email,
                "password": password_hash
            })
            
            if user:
                # Atualiza último login
                users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"last_login": datetime.now()}}
                )
                return {"success": True, "user": user}
            else:
                return {"success": False, "message": "Credenciais inválidas"}
        
        except Exception as e:
            return {"success": False, "message": f"Erro na autenticação: {e}"}
    
    def get_user_by_id(self, user_id):
        """Busca um usuário pelo ID"""
        try:
            from bson import ObjectId
            users_collection = self.db['users']
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            return user
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
    
    # Métodos para dados do dashboard
    def get_dashboard_stats(self):
        """Retorna estatísticas para o dashboard"""
        try:
            stats_collection = self.db['dashboard_stats']
            stats = stats_collection.find_one({"type": "current_stats"})
            
            if not stats:
                # Cria dados padrão se não existirem
                default_stats = {
                    "type": "current_stats",
                    "earnings_monthly": 40000,
                    "earnings_annual": 215000,
                    "tasks_completed": 18,
                    "pending_requests": 18,
                    "updated_at": datetime.now()
                }
                stats_collection.insert_one(default_stats)
                return default_stats
            
            return stats
        
        except Exception as e:
            print(f"Erro ao buscar estatísticas: {e}")
            return {
                "earnings_monthly": 40000,
                "earnings_annual": 215000,
                "tasks_completed": 18,
                "pending_requests": 18
            }
    
    def get_chart_data(self):
        """Retorna dados para os gráficos"""
        try:
            charts_collection = self.db['chart_data']
            chart_data = charts_collection.find_one({"type": "current_charts"})
            
            if not chart_data:
                # Cria dados padrão para gráficos
                default_chart_data = {
                    "type": "current_charts",
                    "area_chart": {
                        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                        "earnings": [0, 10000, 5000, 15000, 10000, 20000]
                    },
                    "bar_chart": {
                        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                        "revenue": [4215, 5312, 6251, 7841, 9821, 14984]
                    },
                    "pie_chart": {
                        "labels": ["Direct", "Social", "Referral"],
                        "values": [55, 30, 15]
                    },
                    "updated_at": datetime.now()
                }
                charts_collection.insert_one(default_chart_data)
                return default_chart_data
            
            return chart_data
        
        except Exception as e:
            print(f"Erro ao buscar dados dos gráficos: {e}")
            return {
                "area_chart": {
                    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    "earnings": [0, 10000, 5000, 15000, 10000, 20000]
                },
                "bar_chart": {
                    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    "revenue": [4215, 5312, 6251, 7841, 9821, 14984]
                },
                "pie_chart": {
                    "labels": ["Direct", "Social", "Referral"],
                    "values": [55, 30, 15]
                }
            }
    
    def get_table_data(self):
        """Retorna dados para as tabelas"""
        try:
            tables_collection = self.db['table_data']
            table_data = list(tables_collection.find({"type": "employee_data"}))
            
            if not table_data:
                # Cria dados padrão para tabelas
                default_table_data = [
                    {
                        "type": "employee_data",
                        "name": "Tiger Nixon",
                        "position": "System Architect",
                        "office": "Edinburgh",
                        "age": 61,
                        "start_date": "2011/04/25",
                        "salary": "$320,800"
                    },
                    {
                        "type": "employee_data",
                        "name": "Garrett Winters",
                        "position": "Accountant",
                        "office": "Tokyo",
                        "age": 63,
                        "start_date": "2011/07/25",
                        "salary": "$170,750"
                    },
                    {
                        "type": "employee_data",
                        "name": "Ashton Cox",
                        "position": "Junior Technical Author",
                        "office": "San Francisco",
                        "age": 66,
                        "start_date": "2009/01/12",
                        "salary": "$86,000"
                    },
                    {
                        "type": "employee_data",
                        "name": "Cedric Kelly",
                        "position": "Senior Javascript Developer",
                        "office": "Edinburgh",
                        "age": 22,
                        "start_date": "2012/03/29",
                        "salary": "$433,060"
                    }
                ]
                tables_collection.insert_many(default_table_data)
                return default_table_data
            
            return table_data
        
        except Exception as e:
            print(f"Erro ao buscar dados das tabelas: {e}")
            return [
                {
                    "name": "Tiger Nixon",
                    "position": "System Architect",
                    "office": "Edinburgh",
                    "age": 61,
                    "start_date": "2011/04/25",
                    "salary": "$320,800"
                }
            ]
    
    def create_route(self, user_id, route_date, route_name, vehicle_type, destination_city, 
                    total_packages, loose_packages, has_helper, is_sunday_holiday, total_value):
        """Cria uma nova rota"""
        try:
            routes_collection = self.db['routes']
            
            route_data = {
                "user_id": user_id,
                "route_date": route_date,
                "route_name": route_name,
                "vehicle_type": vehicle_type,
                "destination_city": destination_city,
                "total_packages": total_packages,
                "loose_packages": loose_packages,
                "has_helper": has_helper,
                "is_sunday_holiday": is_sunday_holiday,
                "total_value": total_value,
                "created_at": datetime.now()
            }
            
            result = routes_collection.insert_one(route_data)
            return {"success": True, "route_id": str(result.inserted_id)}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao criar rota: {e}"}
    
    def get_user_routes(self, user_id, period="current"):
        """
        Busca as rotas de um usuário por período
        period: "current" para quinzena atual, "previous" para quinzena anterior
        """
        try:
            routes_collection = self.db['routes']
            
            # Obtém as datas de início e fim do período
            if period == "current":
                inicio, fim = get_current_fortnight()
            else:
                inicio, fim = get_previous_fortnight()
            
            # Converte para datetime para incluir horário
            inicio_dt = datetime.combine(inicio, datetime.min.time())
            fim_dt = datetime.combine(fim, datetime.max.time())
            
            # Busca rotas do período
            routes = list(routes_collection.find({
                "user_id": user_id,
                "route_date": {
                    "$gte": inicio_dt,
                    "$lte": fim_dt
                }
            }).sort("route_date", -1))
            
            # Converte ObjectId para string e data para datetime
            for route in routes:
                route['_id'] = str(route['_id'])
                if isinstance(route.get('route_date'), str):
                    try:
                        route['route_date'] = datetime.strptime(route['route_date'], '%Y-%m-%d')
                    except ValueError:
                        pass
            
            # Adiciona informações do período
            period_info = {
                "inicio": inicio.strftime('%d/%m/%Y'),
                "fim": fim.strftime('%d/%m/%Y'),
                "quinzena": "1ª Quinzena" if inicio.day == 1 else "2ª Quinzena",
                "mes": inicio.strftime('%B'),
                "ano": inicio.year
            }
            
            return {
                "success": True,
                "routes": routes,
                "period": period_info,
                "total_routes": len(routes),
                "total_value": sum(route.get('total_value', 0) for route in routes)
            }
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar rotas: {e}"}
    
    def get_route_by_id(self, route_id):
        """Busca uma rota específica pelo ID"""
        try:
            from bson import ObjectId
            routes_collection = self.db['routes']
            route = routes_collection.find_one({"_id": ObjectId(route_id)})
            
            if route:
                route['_id'] = str(route['_id'])
                return {"success": True, "route": route}
            else:
                return {"success": False, "message": "Rota não encontrada"}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar rota: {e}"}
    
    def update_route(self, route_id, user_id, route_date, route_name, vehicle_type, destination_city,
                    total_packages, loose_packages, has_helper, is_sunday_holiday, total_value):
        """Atualiza uma rota existente"""
        try:
            from bson import ObjectId
            routes_collection = self.db['routes']
            
            # Verifica se a rota pertence ao usuário
            existing_route = routes_collection.find_one({"_id": ObjectId(route_id), "user_id": user_id})
            if not existing_route:
                return {"success": False, "message": "Rota não encontrada ou não autorizada"}
            
            update_data = {
                "route_date": route_date,
                "route_name": route_name,
                "vehicle_type": vehicle_type,
                "destination_city": destination_city,
                "total_packages": total_packages,
                "loose_packages": loose_packages,
                "has_helper": has_helper,
                "is_sunday_holiday": is_sunday_holiday,
                "total_value": total_value,
                "updated_at": datetime.now()
            }
            
            result = routes_collection.update_one(
                {"_id": ObjectId(route_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Rota atualizada com sucesso"}
            else:
                return {"success": False, "message": "Nenhuma alteração foi feita"}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao atualizar rota: {e}"}
    
    def delete_route(self, route_id, user_id):
        """Deleta uma rota"""
        try:
            from bson import ObjectId
            routes_collection = self.db['routes']
            
            # Verifica se a rota pertence ao usuário
            existing_route = routes_collection.find_one({"_id": ObjectId(route_id), "user_id": user_id})
            if not existing_route:
                return {"success": False, "message": "Rota não encontrada ou não autorizada"}
            
            result = routes_collection.delete_one({"_id": ObjectId(route_id)})
            
            if result.deleted_count > 0:
                return {"success": True, "message": "Rota deletada com sucesso"}
            else:
                return {"success": False, "message": "Erro ao deletar rota"}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao deletar rota: {e}"}

    # Métodos para gerenciamento de despesas
    def create_expense(self, user_id, expense_date, description, category, amount, payment_method, notes=""):
        """Cria uma nova despesa"""
        try:
            expenses_collection = self.db['expenses']
            
            # Converte string de data para objeto datetime
            if isinstance(expense_date, str):
                expense_date = datetime.strptime(expense_date, '%Y-%m-%d')
            
            expense_data = {
                "user_id": user_id,
                "expense_date": expense_date,
                "description": description,
                "category": category,
                "amount": float(amount),
                "payment_method": payment_method,
                "notes": notes,
                "created_at": datetime.now()
            }
            
            result = expenses_collection.insert_one(expense_data)
            return {"success": True, "expense_id": str(result.inserted_id)}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao criar despesa: {e}"}
    
    def get_user_expenses(self, user_id, period="current"):
        """
        Busca as despesas de um usuário por período
        period: "current" para quinzena atual, "previous" para quinzena anterior
        """
        try:
            expenses_collection = self.db['expenses']
            
            # Obtém as datas de início e fim do período
            if period == "current":
                inicio, fim = get_current_fortnight()
            else:
                inicio, fim = get_previous_fortnight()
            
            # Converte para datetime para incluir horário
            inicio_dt = datetime.combine(inicio, datetime.min.time())
            fim_dt = datetime.combine(fim, datetime.max.time())
            
            # Busca despesas do período
            expenses = list(expenses_collection.find({
                "user_id": user_id,
                "expense_date": {
                    "$gte": inicio_dt,
                    "$lte": fim_dt
                }
            }).sort("expense_date", -1))
            
            # Converte ObjectId para string e corrige datas em formato string
            for expense in expenses:
                expense['_id'] = str(expense['_id'])
                
                # Converte string de data para datetime se necessário
                if isinstance(expense.get('expense_date'), str):
                    try:
                        expense['expense_date'] = datetime.strptime(expense['expense_date'], '%Y-%m-%d')
                    except ValueError:
                        # Se não conseguir converter, mantém como string
                        pass
            
            # Adiciona informações do período
            period_info = {
                "inicio": inicio.strftime('%d/%m/%Y'),
                "fim": fim.strftime('%d/%m/%Y'),
                "quinzena": "1ª Quinzena" if inicio.day == 1 else "2ª Quinzena",
                "mes": inicio.strftime('%B'),
                "ano": inicio.year
            }
            
            # Calcula totais por categoria
            categories = {}
            total_amount = 0
            for expense in expenses:
                category = expense.get('category', 'Outros')
                amount = expense.get('amount', 0)
                categories[category] = categories.get(category, 0) + amount
                total_amount += amount
            
            return {
                "success": True,
                "expenses": expenses,
                "period": period_info,
                "total_expenses": total_amount,
                "categories": categories,
                "total_count": len(expenses)
            }
            
        except Exception as e:
            print(f"Erro ao buscar despesas: {e}")
            return {
                "success": False,
                "message": f"Erro ao buscar despesas: {e}",
                "expenses": [],
                "total_expenses": 0,
                "categories": {},
                "total_count": 0
            }
    
    # Métodos para gerenciamento de pacotes dos assistentes
    def get_user_packages(self, user_id, period="current"):
        """
        Busca os pacotes de um usuário por período
        period: "current" para quinzena atual, "previous" para quinzena anterior
        """
        try:
            packages_collection = self.db['assistant_packages']
            
            # Obtém as datas de início e fim do período
            if period == "current":
                inicio, fim = get_current_fortnight()
            else:
                inicio, fim = get_previous_fortnight()
            
            # Converte para datetime para incluir horário
            inicio_dt = datetime.combine(inicio, datetime.min.time())
            fim_dt = datetime.combine(fim, datetime.max.time())
            
            # Busca pacotes do período
            packages = list(packages_collection.find({
                "user_id": user_id,
                "delivery_date": {
                    "$gte": inicio_dt,
                    "$lte": fim_dt
                }
            }).sort("delivery_date", -1))
            
            # Converte ObjectId para string e ajusta datas
            for package in packages:
                package['_id'] = str(package['_id'])
                if isinstance(package.get('delivery_date'), str):
                    try:
                        package['delivery_date'] = datetime.strptime(package['delivery_date'], '%Y-%m-%d')
                    except ValueError:
                        pass
            
            # Adiciona informações do período
            period_info = {
                "inicio": inicio.strftime('%d/%m/%Y'),
                "fim": fim.strftime('%d/%m/%Y'),
                "quinzena": "1ª Quinzena" if inicio.day == 1 else "2ª Quinzena",
                "mes": inicio.strftime('%B'),
                "ano": inicio.year
            }
            
            # Calcula estatísticas
            total_packages = sum(package.get('packages_delivered', 0) for package in packages)
            total_value = sum(package.get('total_value', 0) for package in packages)
            total_stops = sum(package.get('total_stops', 0) for package in packages)
            unique_assistants = len(set(package.get('assistant_name') for package in packages))
            
            return {
                "success": True,
                "packages": packages,
                "period": period_info,
                "total_packages": total_packages,
                "total_value": total_value,
                "total_stops": total_stops,
                "unique_assistants": unique_assistants,
                "avg_per_package": total_value / total_packages if total_packages > 0 else 0
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar pacotes: {e}",
                "packages": [],
                "total_packages": 0,
                "total_value": 0,
                "total_stops": 0,
                "unique_assistants": 0,
                "avg_per_package": 0
            }
    
    def create_package(self, package_data):
        """Cria um novo pacote de assistente"""
        try:
            packages_collection = self.db['assistant_packages']
            
            # Converter a data de entrega para datetime
            if package_data.get('delivery_date'):
                package_data['delivery_date'] = datetime.strptime(package_data['delivery_date'], '%Y-%m-%d')
            
            # Inserir o pacote no banco de dados
            result = packages_collection.insert_one(package_data)
            
            if result.inserted_id:
                return {"success": True, "message": "Pacote criado com sucesso", "package_id": str(result.inserted_id)}
            else:
                return {"success": False, "message": "Erro ao criar pacote"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao criar pacote: {e}"}
    
    def delete_package(self, package_id, user_id):
        """Deleta um pacote de assistente"""
        try:
            from bson import ObjectId
            packages_collection = self.db['assistant_packages']
            
            # Verifica se o pacote pertence ao usuário
            existing_package = packages_collection.find_one({"_id": ObjectId(package_id), "user_id": user_id})
            if not existing_package:
                return {"success": False, "message": "Pacote não encontrado ou não autorizado"}
            
            result = packages_collection.delete_one({"_id": ObjectId(package_id)})
            
            if result.deleted_count > 0:
                return {"success": True, "message": "Pacote deletado com sucesso"}
            else:
                return {"success": False, "message": "Erro ao deletar pacote"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao deletar pacote: {e}"}
    
    def get_expense_by_id(self, expense_id):
        """Busca uma despesa específica pelo ID"""
        try:
            from bson import ObjectId
            expenses_collection = self.db['expenses']
            expense = expenses_collection.find_one({"_id": ObjectId(expense_id)})
            
            if expense:
                expense['_id'] = str(expense['_id'])
            
            return expense
        except Exception as e:
            print(f"Erro ao buscar despesa: {e}")
            return None
    
    def update_expense(self, expense_id, user_id, expense_date, description, category, amount, payment_method, notes=""):
        """Atualiza uma despesa existente"""
        try:
            from bson import ObjectId
            expenses_collection = self.db['expenses']
            
            # Converte string de data para objeto datetime
            if isinstance(expense_date, str):
                expense_date = datetime.strptime(expense_date, '%Y-%m-%d')
            
            update_data = {
                "expense_date": expense_date,
                "description": description,
                "category": category,
                "amount": float(amount),
                "payment_method": payment_method,
                "notes": notes,
                "updated_at": datetime.now()
            }
            
            result = expenses_collection.update_one(
                {"_id": ObjectId(expense_id), "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Despesa atualizada com sucesso"}
            else:
                return {"success": False, "message": "Despesa não encontrada ou não autorizada"}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao atualizar despesa: {e}"}
    
    def delete_expense(self, expense_id, user_id):
        """Deleta uma despesa"""
        try:
            from bson import ObjectId
            expenses_collection = self.db['expenses']
            
            result = expenses_collection.delete_one({
                "_id": ObjectId(expense_id),
                "user_id": user_id
            })
            
            if result.deleted_count > 0:
                return {"success": True, "message": "Despesa deletada com sucesso"}
            else:
                return {"success": False, "message": "Despesa não encontrada ou não autorizada"}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao deletar despesa: {e}"}
    
    def get_expenses_by_category(self, user_id):
        """Retorna despesas agrupadas por categoria para relatórios"""
        try:
            expenses_collection = self.db['expenses']
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$category",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"total": -1}}
            ]
            
            result = list(expenses_collection.aggregate(pipeline))
            return result
        except Exception as e:
            print(f"Erro ao buscar despesas por categoria: {e}")
            return []
    
    def get_monthly_expenses(self, user_id, year=None):
        """Retorna despesas agrupadas por mês para relatórios"""
        try:
            expenses_collection = self.db['expenses']
            
            if year is None:
                year = datetime.now().year
            
            pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "expense_date": {
                        "$gte": f"{year}-01-01",
                        "$lt": f"{year + 1}-01-01"
                    }
                }},
                {"$group": {
                    "_id": {"$substr": ["$expense_date", 0, 7]},  # YYYY-MM
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            result = list(expenses_collection.aggregate(pipeline))
            return result
        except Exception as e:
            print(f"Erro ao buscar despesas mensais: {e}")
            return []
    
    # Métodos para perfil do usuário
    def update_user_profile(self, user_id, profile_data):
        """Atualiza dados do perfil do usuário"""
        try:
            from bson import ObjectId
            users_collection = self.db['users']
            
            result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": profile_data}
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Perfil atualizado com sucesso"}
            else:
                return {"success": False, "message": "Nenhuma alteração foi feita"}
                
        except Exception as e:
            return {"success": False, "message": f"Erro ao atualizar perfil: {e}"}
    
    def update_user_password(self, user_id, new_password):
        """Atualiza a senha do usuário"""
        try:
            from bson import ObjectId
            users_collection = self.db['users']
            
            # Hash da nova senha
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password": password_hash}}
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Senha atualizada com sucesso"}
            else:
                return {"success": False, "message": "Erro ao atualizar senha"}
                
        except Exception as e:
            return {"success": False, "message": f"Erro ao atualizar senha: {e}"}
    
    def count_user_routes(self, user_id):
        """Conta o total de rotas do usuário"""
        try:
            from bson import ObjectId
            routes_collection = self.db['routes']
            count = routes_collection.count_documents({"user_id": ObjectId(user_id)})
            return count
        except Exception as e:
            print(f"Erro ao contar rotas: {e}")
            return 0
    
    def count_user_expenses(self, user_id):
        """Conta o total de despesas do usuário"""
        try:
            from bson import ObjectId
            expenses_collection = self.db['expenses']
            count = expenses_collection.count_documents({"user_id": ObjectId(user_id)})
            return count
        except Exception as e:
            print(f"Erro ao contar despesas: {e}")
            return 0
    
    # Métodos para pacotes de assistentes
    def create_assistant_package(self, user_id, assistant_name, delivery_date, total_stops, packages_delivered, value_per_stop, total_value, observations=""):
        """Cria um novo registro de pacotes para assistente"""
        try:
            from bson import ObjectId
            assistant_packages_collection = self.db['assistant_packages']
            
            package_data = {
                "user_id": ObjectId(user_id),
                "assistant_name": assistant_name,
                "delivery_date": delivery_date,
                "total_stops": total_stops,
                "packages_delivered": packages_delivered,
                "value_per_stop": value_per_stop,
                "total_value": total_value,
                "observations": observations,
                "created_at": datetime.now()
            }
            
            result = assistant_packages_collection.insert_one(package_data)
            return {"success": True, "package_id": str(result.inserted_id)}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao cadastrar pacotes: {e}"}
    
    def get_user_assistant_packages(self, user_id):
        """Busca todos os pacotes de assistentes do usuário"""
        try:
            from bson import ObjectId
            assistant_packages_collection = self.db['assistant_packages']
            
            packages = list(assistant_packages_collection.find(
                {"user_id": ObjectId(user_id)}
            ).sort("delivery_date", -1))
            
            # Converter ObjectId para string para serialização
            for package in packages:
                package['_id'] = str(package['_id'])
                package['user_id'] = str(package['user_id'])
            
            return {"success": True, "packages": packages}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar pacotes: {e}", "packages": []}
    
    def delete_assistant_package(self, package_id, user_id):
        """Deleta um registro de pacotes de assistente"""
        try:
            from bson import ObjectId
            assistant_packages_collection = self.db['assistant_packages']
            
            result = assistant_packages_collection.delete_one({
                "_id": ObjectId(package_id),
                "user_id": ObjectId(user_id)
            })
            
            if result.deleted_count > 0:
                return {"success": True, "message": "Pacote deletado com sucesso"}
            else:
                return {"success": False, "message": "Pacote não encontrado"}
        
        except Exception as e:
            return {"success": False, "message": f"Erro ao deletar pacote: {e}"}

# Instância global do gerenciador de banco de dados
db_manager = DatabaseManager()