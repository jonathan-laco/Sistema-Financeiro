from models import Transaction, BankAccount, Category, Invoice
from extensions import db
from datetime import datetime
from sqlalchemy import extract
from utils.date_helpers import get_now_sp
from uuid import uuid4
import calendar

def get_user_transactions(user_id, filters=None, page=1, per_page=20):
    """
    Retorna as transações de um usuário com filtros e paginação
    """
    query = Transaction.query.filter_by(user_id=user_id, is_deleted=False)
    
    if filters:
        if 'account_id' in filters and filters['account_id']:
            query = query.filter_by(account_id=filters['account_id'])
        if 'type' in filters and filters['type']:
            query = query.filter_by(type=filters['type'])
        if 'status' in filters and filters['status']:
            query = query.filter_by(status=filters['status'])
        if 'category_id' in filters and filters['category_id']:
            query = query.filter_by(category_id=filters['category_id'])
        if 'month' in filters and 'year' in filters:
            query = query.filter(
                extract('month', Transaction.date) == filters['month'],
                extract('year', Transaction.date) == filters['year']
            )
        if 'is_mei_transaction' in filters:
            query = query.filter_by(is_mei_transaction=filters['is_mei_transaction'])
        if 'has_invoice' in filters:
            query = query.filter_by(has_invoice=filters['has_invoice'])
    
    return query.order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

def get_all_user_transactions(user_id, filters=None):
    """
    Retorna todas as transações de um usuário com filtros, sem paginação
    Usado para relatórios de impressão
    """
    query = Transaction.query.filter_by(user_id=user_id, is_deleted=False)
    
    if filters:
        if 'account_id' in filters and filters['account_id']:
            query = query.filter_by(account_id=filters['account_id'])
        if 'type' in filters and filters['type']:
            query = query.filter_by(type=filters['type'])
        if 'status' in filters and filters['status']:
            query = query.filter_by(status=filters['status'])
        if 'category_id' in filters and filters['category_id']:
            query = query.filter_by(category_id=filters['category_id'])
        if 'month' in filters and 'year' in filters:
            query = query.filter(
                extract('month', Transaction.date) == filters['month'],
                extract('year', Transaction.date) == filters['year']
            )
        if 'is_mei_transaction' in filters:
            query = query.filter_by(is_mei_transaction=filters['is_mei_transaction'])
        if 'has_invoice' in filters:
            query = query.filter_by(has_invoice=filters['has_invoice'])
    
    return query.order_by(Transaction.date.desc()).all()

def get_transaction_by_id(transaction_id, user_id):
    """
    Retorna uma transação específica de um usuário
    """
    return Transaction.query.filter_by(id=transaction_id, user_id=user_id, is_deleted=False).first()

def create_transaction(user_id, account_id, category_id, transaction_type, amount, description, is_confirmed=True, is_mei_transaction=False, transaction_date=None, installment_info=None):
    """
    Cria uma nova transação
    """
    # Verificar se a conta pertence ao usuário
    account = BankAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return None, "Conta inválida"
    
    # Verificar se a categoria pertence ao usuário e está ativa
    category = Category.query.filter_by(id=category_id, user_id=user_id, is_active=True).first()
    if not category:
        return None, "Categoria inválida"
    
    # Verificar se o tipo da categoria corresponde ao tipo da transação
    if category.type != transaction_type:
        return None, f"A categoria selecionada não é válida para {transaction_type}"
    
    # Definir status
    status = 'confirmado' if is_confirmed else 'pendente'
    
    # Usar a data fornecida ou obter a data atual correta
    if transaction_date is None:
        transaction_date = get_now_sp()
    
    # Criar nova transação
    new_transaction = Transaction(
        user_id=user_id,
        account_id=account_id,
        category_id=category_id,
        type=transaction_type,
        amount=amount,
        description=description,
        status=status,
        is_confirmed=is_confirmed,
        date=transaction_date,
        is_mei_transaction=is_mei_transaction,
        has_invoice=False
    )

    if installment_info:
        new_transaction.installment_group_id = installment_info.get('group_id')
        new_transaction.installment_number = installment_info.get('number')
        new_transaction.installment_total = installment_info.get('total')
        new_transaction.is_salary_deductible = installment_info.get('is_salary_deductible', False)
        new_transaction.salary_deduction_day = installment_info.get('salary_deduction_day')
    
    db.session.add(new_transaction)
    
    # Atualizar saldo da conta se a transação for confirmada
    if status == 'confirmado':
        if transaction_type == 'receita':
            account.balance += amount
        else:  # despesa
            account.balance -= amount
    
    db.session.commit()
    return new_transaction, "Transação adicionada com sucesso"

def create_installment_transactions(user_id, account_id, category_id, amount, description, installments, is_confirmed=True, is_mei_transaction=False, first_date=None, is_salary_deductible=False, salary_deduction_day=None):
    """
    Cria transações de despesa parcelada, dividindo o valor total em parcelas mensais.
    """
    account = BankAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return None, "Conta inválida"

    category = Category.query.filter_by(id=category_id, user_id=user_id, is_active=True).first()
    if not category:
        return None, "Categoria inválida"

    if category.type != 'despesa':
        return None, "A categoria selecionada não é válida para despesa"

    if installments < 2:
        return None, "Informe pelo menos 2 parcelas"

    if amount <= 0:
        return None, "Informe um valor válido"

    if is_salary_deductible:
        if not salary_deduction_day or salary_deduction_day < 1 or salary_deduction_day > 31:
            return None, "Informe um dia de salário entre 1 e 31"

    if first_date is None:
        first_date = get_now_sp()

    group_id = str(uuid4())
    total_cents = int(round(amount * 100))
    base_cents = total_cents // installments
    remainder = total_cents % installments
    created_transactions = []
    status = 'confirmado' if is_confirmed else 'pendente'

    try:
        for index in range(installments):
            parcel_cents = base_cents + (1 if index < remainder else 0)
            parcel_amount = parcel_cents / 100
            parcel_date = _add_months(first_date, index, salary_deduction_day if is_salary_deductible else None)
            parcel_description = f"{description} ({index + 1}/{installments})"

            transaction = Transaction(
                user_id=user_id,
                account_id=account_id,
                category_id=category_id,
                type='despesa',
                amount=parcel_amount,
                description=parcel_description,
                status=status,
                is_confirmed=is_confirmed,
                date=parcel_date,
                is_mei_transaction=is_mei_transaction,
                has_invoice=False,
                installment_group_id=group_id,
                installment_number=index + 1,
                installment_total=installments,
                is_salary_deductible=is_salary_deductible,
                salary_deduction_day=salary_deduction_day if is_salary_deductible else None
            )

            db.session.add(transaction)
            created_transactions.append(transaction)

        if status == 'confirmado':
            account.balance -= amount

        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return None, f"Erro ao criar parcelas: {str(exc)}"

    return created_transactions, f"{installments} parcelas cadastradas com sucesso"

def _add_months(base_date, months_to_add, preferred_day=None):
    """
    Soma meses preservando o horário e ajustando o dia para o último dia válido do mês.
    """
    month_index = base_date.month - 1 + months_to_add
    year = base_date.year + month_index // 12
    month = month_index % 12 + 1
    day = preferred_day or base_date.day
    last_day = calendar.monthrange(year, month)[1]
    return base_date.replace(year=year, month=month, day=min(day, last_day))

def update_transaction(transaction_id, user_id, account_id, category_id, transaction_type, amount, description, is_confirmed, is_mei_transaction=None):
    """
    Atualiza uma transação existente
    """
    # Buscar a transação
    transaction = get_transaction_by_id(transaction_id, user_id)
    if not transaction:
        return None, "Transação não encontrada"
    
    # Verificar se a conta pertence ao usuário
    account = BankAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return None, "Conta inválida"
    
    # Verificar se a categoria pertence ao usuário e está ativa
    category = Category.query.filter_by(id=category_id, user_id=user_id, is_active=True).first()
    if not category:
        return None, "Categoria inválida"
    
    # Verificar se o tipo da categoria corresponde ao tipo da transação
    if category.type != transaction_type:
        return None, f"A categoria selecionada não é válida para {transaction_type}"
    
    # Definir status
    new_status = 'confirmado' if is_confirmed else 'pendente'
    
    # Se a transação estava confirmada, reverter o efeito no saldo da conta original
    if transaction.status == 'confirmado':
        old_account = BankAccount.query.get(transaction.account_id)
        if transaction.type == 'receita':
            old_account.balance -= transaction.amount
        else:  # despesa
            old_account.balance += transaction.amount
    
    # Atualizar a transação
    transaction.account_id = account_id
    transaction.type = transaction_type
    transaction.amount = amount
    transaction.description = description
    transaction.category_id = category_id
    transaction.status = new_status
    transaction.is_confirmed = is_confirmed
    
    # Atualizar flag MEI se fornecido
    if is_mei_transaction is not None:
        transaction.is_mei_transaction = is_mei_transaction
    
    # Se a transação agora está confirmada, atualizar o saldo da nova conta
    if new_status == 'confirmado':
        if transaction_type == 'receita':
            account.balance += amount
        else:  # despesa
            account.balance -= amount
    
    db.session.commit()
    return transaction, "Transação atualizada com sucesso"

def delete_transaction(transaction_id, user_id):
    """
    Exclui uma transação
    """
    transaction = get_transaction_by_id(transaction_id, user_id)
    if not transaction:
        return False, "Transação não encontrada"
    
    # Se a transação estava confirmada, reverter o efeito no saldo da conta
    if transaction.status == 'confirmado':
        account = BankAccount.query.get(transaction.account_id)
        if transaction.type == 'receita':
            account.balance -= transaction.amount
        else:  # despesa
            account.balance += transaction.amount
    
    # Verificar se há nota fiscal associada
    invoice = Invoice.query.filter_by(transaction_id=transaction_id).first()
    if invoice:
        # Excluir arquivo
        from services.invoice_service import delete_invoice
        delete_invoice(invoice.id, user_id)
    
    # Marcar como deletada (soft-delete)
    transaction.is_deleted = True
    transaction.deleted_at = datetime.utcnow()
    db.session.commit()
    return True, "Transação excluída com sucesso"

def confirm_transaction(transaction_id, user_id):
    """
    Confirma uma transação pendente
    """
    transaction = get_transaction_by_id(transaction_id, user_id)
    if not transaction:
        return False, "Transação não encontrada"
    
    if transaction.status != 'pendente':
        return False, "Apenas transações pendentes podem ser confirmadas"
    
    # Atualizar status da transação
    transaction.status = 'confirmado'
    transaction.is_confirmed = True
    
    # Atualizar saldo da conta
    account = BankAccount.query.get(transaction.account_id)
    if transaction.type == 'receita':
        account.balance += transaction.amount
    else:  # despesa
        account.balance -= transaction.amount
    
    db.session.commit()
    return True, "Transação confirmada com sucesso"

def cancel_transaction(transaction_id, user_id):
    """
    Cancela uma transação pendente
    """
    transaction = get_transaction_by_id(transaction_id, user_id)
    if not transaction:
        return False, "Transação não encontrada"
    
    if transaction.status != 'pendente':
        return False, "Apenas transações pendentes podem ser canceladas"
    
    # Atualizar status da transação
    transaction.status = 'cancelado'
    
    db.session.commit()
    return True, "Transação cancelada com sucesso"

def get_recent_transactions(user_id, limit=5):
    """
    Retorna as transações mais recentes de um usuário
    """
    return Transaction.query.filter_by(user_id=user_id, is_deleted=False).order_by(Transaction.date.desc()).limit(limit).all()

def get_pending_transactions(user_id):
    """
    Retorna as transações pendentes de um usuário
    """
    return Transaction.query.filter_by(user_id=user_id, status='pendente', is_deleted=False).order_by(Transaction.date.desc()).all()

def calculate_monthly_totals(user_id, month, year, is_mei_only=False):
    """
    Calcula os totais de receitas e despesas de um mês específico
    """
    query = Transaction.query.filter_by(
        user_id=user_id,
        status='confirmado',
        is_deleted=False
    ).filter(
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year
    )
    
    if is_mei_only:
        query = query.filter_by(is_mei_transaction=True)
    
    transactions = query.all()
    
    total_income = sum(t.amount for t in transactions if t.type == 'receita')
    total_expense = sum(t.amount for t in transactions if t.type == 'despesa')
    
    return total_income, total_expense

def count_all_user_transactions(user_id):
    """
    Retorna o número total de transações de um usuário
    """
    return Transaction.query.filter_by(user_id=user_id, is_deleted=False).count()

def count_filtered_transactions(user_id, filters=None):
    """
    Retorna o número de transações de um usuário com filtros aplicados
    """
    query = Transaction.query.filter_by(user_id=user_id, is_deleted=False)
    
    if filters:
        if 'account_id' in filters and filters['account_id']:
            query = query.filter_by(account_id=filters['account_id'])
        if 'type' in filters and filters['type']:
            query = query.filter_by(type=filters['type'])
        if 'status' in filters and filters['status']:
            query = query.filter_by(status=filters['status'])
        if 'category_id' in filters and filters['category_id']:
            query = query.filter_by(category_id=filters['category_id'])
        if 'month' in filters and 'year' in filters:
            query = query.filter(
                extract('month', Transaction.date) == filters['month'],
                extract('year', Transaction.date) == filters['year']
            )
        if 'is_mei_transaction' in filters:
            query = query.filter_by(is_mei_transaction=filters['is_mei_transaction'])
        if 'has_invoice' in filters:
            query = query.filter_by(has_invoice=filters['has_invoice'])
    
    return query.count()

def get_mei_transactions(user_id, page=1, per_page=20):
    """
    Retorna as transações MEI de um usuário
    """
    return Transaction.query.filter_by(
        user_id=user_id,
        is_mei_transaction=True,
        is_deleted=False
    ).order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

def calculate_mei_totals(user_id, month, year):
    """
    Calcula os totais de receitas e despesas MEI de um mês específico
    """
    transactions = Transaction.query.filter_by(
        user_id=user_id,
        status='confirmado',
        is_mei_transaction=True
    ).filter(
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.type == 'receita')
    total_expense = sum(t.amount for t in transactions if t.type == 'despesa')
    
    return total_income, total_expense
