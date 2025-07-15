# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
import database
import math # Precisamos do módulo math para calcular o teto (ceil)

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui' # Chave secreta para sessões e mensagens flash

# Definir quantos itens por página
ITEMS_PER_PAGE = 5

# Rota para a página inicial (listar funcionários)
@app.route('/')
@app.route('/page/<int:page>') # Nova rota para paginação
def index(page=1): # Valor padrão da página é 1
    # Obter o total de funcionários
    total_employees = database.get_total_employees_count()
    
    # Calcular o número total de páginas
    # math.ceil arredonda para cima, garantindo que mesmo um único item extra tenha sua própria página
    total_pages = math.ceil(total_employees / ITEMS_PER_PAGE)

    # Obter os funcionários para a página atual
    employees = database.get_paginated_employees(page, ITEMS_PER_PAGE)

    return render_template(
        'index.html',
        employees=employees,
        current_page=page,
        total_pages=total_pages,
        items_per_page=ITEMS_PER_PAGE,
        total_employees=total_employees
    )

# ... (Mantenha as rotas add_employee, edit_employee, delete_employee inalteradas)

# Rota para adicionar um novo funcionário (GET e POST)
@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']

        if not name or not email:
            flash('Nome e Email são campos obrigatórios!', 'danger')
            return render_template('add_edit.html', employee=None)
        
        employee_id = database.create_employee(name, email, address, phone)
        if employee_id:
            flash('Funcionário adicionado com sucesso!', 'success')
            # Após adicionar, redireciona para a primeira página da lista
            return redirect(url_for('index', page=1))
        else:
            flash(f'Erro ao adicionar funcionário. Verifique se o email já existe.', 'danger')
            return render_template('add_edit.html', employee={'name': name, 'email': email, 'address': address, 'phone': phone})
    
    return render_template('add_edit.html', employee=None)

# Rota para editar um funcionário (GET e POST)
@app.route('/edit/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    employee = database.get_employee_by_id(employee_id)
    if not employee:
        flash('Funcionário não encontrado!', 'danger')
        return redirect(url_for('index', page=1)) # Redireciona para a primeira página
    # ... (o resto da função edit_employee)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']

        if not name or not email:
            flash('Nome e Email são campos obrigatórios!', 'danger')
            return render_template('add_edit.html', employee=employee)
        
        updated = database.update_employee(employee_id, name, email, address, phone)
        if updated:
            flash('Funcionário atualizado com sucesso!', 'success')
            return redirect(url_for('index', page=request.args.get('current_page', 1))) # Tenta voltar para a página atual
        else:
            flash('Erro ao atualizar funcionário. Verifique se o email já existe.', 'danger')
            return render_template('add_edit.html', employee={'id': employee_id, 'name': name, 'email': email, 'address': address, 'phone': phone})
    
    return render_template('add_edit.html', employee=employee)

# Rota para deletar um funcionário
@app.route('/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    deleted = database.delete_employee(employee_id)
    if deleted:
        flash('Funcionário excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir funcionário.', 'danger')
    
    # Após deletar, redireciona para a página atual ou para a primeira se não houver mais itens na página
    current_page = request.args.get('current_page', 1, type=int)
    total_employees_after_delete = database.get_total_employees_count()
    total_pages_after_delete = math.ceil(total_employees_after_delete / ITEMS_PER_PAGE)

    # Se a página atual for maior que o novo total de páginas, vá para a última página válida
    if current_page > total_pages_after_delete and total_pages_after_delete > 0:
        current_page = total_pages_after_delete
    elif total_pages_after_delete == 0: # Se não houver mais funcionários, volte para a página 1 (vazia)
        current_page = 1

    return redirect(url_for('index', page=current_page))

if __name__ == '__main__':
    app.run(debug=True)