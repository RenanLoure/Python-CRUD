# database.py

import psycopg2
from psycopg2 import extras

# Configurações do banco de dados
DB_HOST = "localhost"
DB_NAME = "PythonBaseProjects"
DB_USER = "Admin" # Mude para o usuário que você definiu
DB_PASS = "1299" # Mude para a senha que você definiu
DB_PORT = "5433" # Sua porta correta

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            #client_encoding='UTF8' # Força a codificação do cliente para UTF8
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# --- NOVAS FUNÇÕES PARA PAGINAÇÃO ---

def get_paginated_employees(page, per_page):
    """
    Retorna uma lista de funcionários para a página especificada.
    page: número da página (começando de 1)
    per_page: número de itens por página
    """
    conn = get_db_connection()
    employees = []
    if conn:
        try:
            offset = (page - 1) * per_page
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    "SELECT id, name, email, address, phone FROM employees ORDER BY id DESC LIMIT %s OFFSET %s",
                    (per_page, offset)
                )
                employees = cur.fetchall()
                return [dict(employee) for employee in employees]
        except Exception as e:
            print(f"Erro ao buscar funcionários paginados: {e}")
            return []
        finally:
            conn.close()
    return []

def get_total_employees_count():
    """Retorna o número total de funcionários no banco de dados."""
    conn = get_db_connection()
    count = 0
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM employees")
                count = cur.fetchone()[0]
                return count
        except Exception as e:
            print(f"Erro ao contar funcionários: {e}")
            return 0
        finally:
            conn.close()
    return 0

# --- FUNÇÕES EXISTENTES (get_all_employees pode ser removida ou mantida se usada em outro lugar) ---

# Você pode remover esta função se não for mais usada diretamente,
# já que usaremos a get_paginated_employees agora.
def get_all_employees():
    """Retorna todos os funcionários do banco de dados."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT id, name, email, address, phone FROM employees ORDER BY id DESC")
                employees = cur.fetchall()
                return [dict(employee) for employee in employees]
        except Exception as e:
            print(f"Erro ao buscar funcionários: {e}")
            return []
        finally:
            conn.close()
    return []

# ... (Mantenha as funções create_employee, get_employee_by_id, update_employee, delete_employee inalteradas)
def create_employee(name, email, address, phone):
    """Insere um novo funcionário no banco de dados."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO employees (name, email, address, phone) VALUES (%s, %s, %s, %s) RETURNING id",
                    (name, email, address, phone)
                )
                employee_id = cur.fetchone()[0]
                conn.commit()
                return employee_id
        except psycopg2.IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e):
                print(f"Erro: Email '{email}' já existe.")
                return None
            else:
                raise e
        except Exception as e:
            conn.rollback()
            print(f"Erro ao criar funcionário: {e}")
            return None
        finally:
            conn.close()
    return None

def get_employee_by_id(employee_id):
    """Retorna um funcionário pelo ID."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT id, name, email, address, phone FROM employees WHERE id = %s", (employee_id,))
                employee = cur.fetchone()
                return dict(employee) if employee else None
        except Exception as e:
            print(f"Erro ao buscar funcionário por ID: {e}")
            return None
        finally:
            conn.close()
    return None

def update_employee(employee_id, name, email, address, phone):
    """Atualiza um funcionário existente."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE employees SET name = %s, email = %s, address = %s, phone = %s WHERE id = %s",
                    (name, email, address, phone, employee_id)
                )
                conn.commit()
                return cur.rowcount > 0
        except psycopg2.IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e):
                print(f"Erro: Email '{email}' já existe para outro funcionário.")
                return False
            else:
                raise e
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar funcionário: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_employee(employee_id):
    """Exclui um funcionário pelo ID."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao deletar funcionário: {e}")
            return False
        finally:
            conn.close()
    return False