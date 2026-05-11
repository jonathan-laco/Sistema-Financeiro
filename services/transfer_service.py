from datetime import datetime

from extensions import db
from models import BankAccount, Transfer
from utils.date_helpers import get_now_sp


def get_user_transfers(user_id, limit=None):
    query = Transfer.query.filter_by(user_id=user_id, is_deleted=False).order_by(Transfer.date.desc())
    if limit:
        return query.limit(limit).all()
    return query.all()


def get_transfer_by_id(transfer_id, user_id):
    return Transfer.query.filter_by(id=transfer_id, user_id=user_id, is_deleted=False).first()


def create_transfer(user_id, from_account_id, to_account_id, amount, description=None, is_confirmed=True, transfer_date=None):
    from_account = BankAccount.query.filter_by(id=from_account_id, user_id=user_id, is_deleted=False).first()
    if not from_account:
        return None, "Conta de origem inválida"

    to_account = BankAccount.query.filter_by(id=to_account_id, user_id=user_id, is_deleted=False).first()
    if not to_account:
        return None, "Conta de destino inválida"

    if from_account.id == to_account.id:
        return None, "A conta de origem deve ser diferente da conta de destino"

    if amount is None or amount <= 0:
        return None, "Informe um valor maior que zero"

    if transfer_date is None:
        transfer_date = get_now_sp()

    status = 'confirmado' if is_confirmed else 'pendente'
    transfer = Transfer(
        user_id=user_id,
        from_account_id=from_account.id,
        to_account_id=to_account.id,
        amount=amount,
        description=description,
        date=transfer_date,
        is_confirmed=is_confirmed,
        status=status
    )

    db.session.add(transfer)

    if status == 'confirmado':
        from_account.balance -= amount
        to_account.balance += amount

    db.session.commit()
    return transfer, "Transferência registrada com sucesso"


def confirm_transfer(transfer_id, user_id):
    transfer = get_transfer_by_id(transfer_id, user_id)
    if not transfer:
        return False, "Transferência não encontrada"

    if transfer.status != 'pendente':
        return False, "Apenas transferências pendentes podem ser confirmadas"

    transfer.status = 'confirmado'
    transfer.is_confirmed = True
    transfer.from_account.balance -= transfer.amount
    transfer.to_account.balance += transfer.amount

    db.session.commit()
    return True, "Transferência confirmada com sucesso"


def delete_transfer(transfer_id, user_id):
    transfer = get_transfer_by_id(transfer_id, user_id)
    if not transfer:
        return False, "Transferência não encontrada"

    if transfer.status == 'confirmado':
        transfer.from_account.balance += transfer.amount
        transfer.to_account.balance -= transfer.amount

    transfer.is_deleted = True
    transfer.deleted_at = datetime.utcnow()
    db.session.commit()
    return True, "Transferência excluída com sucesso"
