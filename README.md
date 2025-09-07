# SB Admin 2 - Kivy Dashboard Application

Uma aplicação de dashboard moderna desenvolvida em Python com Kivy, integrada ao MongoDB para gerenciamento de dados em tempo real.

## 🚀 Características

- **Interface Moderna**: Dashboard responsivo inspirado no SB Admin 2
- **Autenticação Segura**: Sistema de login e registro com MongoDB
- **Gráficos Interativos**: Visualizações de dados usando Matplotlib
- **Dados em Tempo Real**: Integração completa com MongoDB Atlas
- **Navegação Intuitiva**: Sidebar com navegação entre diferentes seções
- **Cards Informativos**: Estatísticas atualizadas dinamicamente

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conexão com internet (para MongoDB Atlas)
- Sistema operacional: Windows, macOS ou Linux

## 🔧 Instalação

### 1. Clone ou baixe o projeto
```bash
git clone <url-do-repositorio>
cd aula1
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Instale o garden matplotlib
```bash
garden install matplotlib
```

### 4. Execute a aplicação
```bash
python main.py
```

## 🗄️ Configuração do Banco de Dados

A aplicação está configurada para usar MongoDB Atlas com a seguinte string de conexão:
```
mongodb+srv://ayslano37:Walkingtonn1@demolicao.fk6aapp.mongodb.net/
```

### Estrutura do Banco de Dados

O sistema cria automaticamente as seguintes coleções:

#### `users`
- `email`: Email do usuário
- `password`: Senha criptografada (SHA256)
- `name`: Nome do usuário
- `created_at`: Data de criação
- `last_login`: Último login

#### `dashboard_stats`
- `type`: "current_stats"
- `earnings_monthly`: Ganhos mensais
- `earnings_annual`: Ganhos anuais
- `tasks_completed`: Tarefas completadas
- `pending_requests`: Solicitações pendentes

#### `chart_data`
- `type`: "current_charts"
- `area_chart`: Dados para gráfico de área
- `bar_chart`: Dados para gráfico de barras
- `pie_chart`: Dados para gráfico de pizza

#### `table_data`
- `type`: "employee_data"
- `name`: Nome do funcionário
- `position`: Cargo
- `office`: Escritório
- `age`: Idade
- `start_date`: Data de início
- `salary`: Salário

## 🎯 Como Usar

### 1. Tela de Login
- **Primeiro Acesso**: Clique em "Criar Conta" para registrar um novo usuário
- **Login**: Digite email e senha para acessar o dashboard
- **Validação**: O sistema valida credenciais no MongoDB

### 2. Dashboard Principal
- **Cards Informativos**: Visualize estatísticas em tempo real
- **Navegação**: Use a sidebar para navegar entre seções
- **Dados Dinâmicos**: Informações carregadas diretamente do MongoDB

### 3. Seção de Gráficos
- **Gráfico de Área**: Ganhos ao longo do tempo
- **Gráfico de Barras**: Receita por mês
- **Gráfico de Pizza**: Fontes de receita
- **Dados Atualizados**: Gráficos gerados com dados do banco

### 4. Seção de Tabelas
- **Dados de Funcionários**: Lista completa com informações
- **Dados Dinâmicos**: Informações carregadas do MongoDB
- **Interface Limpa**: Tabela organizada e fácil de ler

## 📁 Estrutura do Projeto

```
aula1/
├── main.py              # Arquivo principal da aplicação
├── database.py          # Gerenciador de conexão MongoDB
├── charts_tables.py     # Telas de gráficos e tabelas
├── requirements.txt     # Dependências do projeto
├── README.md           # Este arquivo
└── __pycache__/        # Cache do Python
```

## 🔧 Dependências

- **kivy>=2.1.0**: Framework para interface gráfica
- **matplotlib>=3.5.0**: Biblioteca para gráficos
- **numpy>=1.21.0**: Computação numérica
- **Pillow>=8.3.0**: Processamento de imagens
- **kivymd>=1.1.0**: Componentes Material Design
- **kivy-garden>=0.1.4**: Extensões do Kivy
- **pymongo>=4.0.0**: Driver MongoDB para Python

## 🚨 Solução de Problemas

### Erro de Conexão MongoDB
- Verifique sua conexão com internet
- Confirme se as credenciais estão corretas
- Teste a conectividade com MongoDB Atlas

### Erro ao Instalar Dependências
```bash
# Atualize o pip
pip install --upgrade pip

# Instale dependências uma por vez
pip install kivy
pip install matplotlib
pip install pymongo
```

### Erro com Garden Matplotlib
```bash
# Reinstale o garden
pip uninstall kivy-garden
pip install kivy-garden
garden install matplotlib
```

## 🔐 Segurança

- Senhas são criptografadas usando SHA256
- Validação de entrada em todos os formulários
- Conexão segura com MongoDB Atlas (SSL/TLS)
- Tratamento de erros para evitar vazamento de informações

## 🎨 Personalização

### Modificar Cores
Edite as cores nos arquivos `main.py` e `charts_tables.py`:
```python
# Exemplo de cor personalizada
background_color=(0.26, 0.59, 0.98, 1)  # Azul
```

### Adicionar Novos Dados
Modifique o arquivo `database.py` para incluir novas coleções:
```python
def get_custom_data(self):
    collection = self.db['custom_collection']
    return collection.find({})
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção de solução de problemas
2. Consulte a documentação do Kivy: https://kivy.org/doc/stable/
3. Documentação do MongoDB: https://docs.mongodb.com/

## 📄 Licença

Este projeto é baseado no template SB Admin 2 e está disponível para uso educacional e comercial.

---

**Desenvolvido com ❤️ usando Python, Kivy e MongoDB**