from datetime import datetime, timedelta
import secrets

from extensions import db
from models import TelegramToken, User


VALID_STATUSES = ('none', 'pending', 'approved', 'rejected', 'disabled')


def get_user_token(user_id):
    return TelegramToken.query.filter_by(user_id=user_id).first()


def get_or_create_user_token(user_id):
    token = get_user_token(user_id)
    if token:
        return token

    token = TelegramToken(user_id=user_id, request_status='none')
    db.session.add(token)
    db.session.commit()
    return token


def _generate_unique_token():
    while True:
        value = secrets.token_hex(32)
        exists = TelegramToken.query.filter_by(token=value).first()
        if not exists:
            return value


def request_access(user_id):
    token = get_or_create_user_token(user_id)

    if token.request_status == 'approved' and token.is_valid:
        return token, 'Seu acesso ao bot já está aprovado.'

    if token.request_status == 'pending':
        return token, 'Sua solicitação já está aguardando aprovação.'

    token.request_status = 'pending'
    token.token = None
    token.telegram_chat_id = None
    token.telegram_username = None
    token.requested_at = datetime.utcnow()
    token.approved_at = None
    token.rejected_at = None
    token.expires_at = None
    token.admin_note = None
    db.session.commit()
    return token, 'Solicitação enviada. Assim que o admin aprovar, seu token aparecerá aqui.'


def approve_request(token_id, expires_days=30, admin_note=None):
    token = TelegramToken.query.get(token_id)
    if not token:
        return None, 'Solicitação não encontrada.'

    try:
        expires_days = int(expires_days)
    except (TypeError, ValueError):
        expires_days = 30

    expires_days = max(1, min(expires_days, 365))
    now = datetime.utcnow()

    token.request_status = 'approved'
    token.token = _generate_unique_token()
    token.expires_days = expires_days
    token.expires_at = now + timedelta(days=expires_days)
    token.approved_at = now
    token.rejected_at = None
    token.telegram_chat_id = None
    token.telegram_username = None
    token.admin_note = admin_note
    db.session.commit()
    return token, 'Token aprovado e gerado com sucesso.'


def reject_request(token_id, admin_note=None):
    token = TelegramToken.query.get(token_id)
    if not token:
        return None, 'Solicitação não encontrada.'

    token.request_status = 'rejected'
    token.token = None
    token.expires_at = None
    token.rejected_at = datetime.utcnow()
    token.telegram_chat_id = None
    token.telegram_username = None
    token.admin_note = admin_note
    db.session.commit()
    return token, 'Solicitação rejeitada.'


def disable_token(token_id, admin_note=None):
    token = TelegramToken.query.get(token_id)
    if not token:
        return None, 'Token não encontrado.'

    token.request_status = 'disabled'
    token.telegram_chat_id = None
    token.telegram_username = None
    token.admin_note = admin_note
    db.session.commit()
    return token, 'Token desativado com sucesso.'


def update_expiration(token_id, expires_days):
    token = TelegramToken.query.get(token_id)
    if not token:
        return None, 'Token não encontrado.'

    try:
        expires_days = int(expires_days)
    except (TypeError, ValueError):
        return None, 'Informe uma quantidade de dias válida.'

    expires_days = max(1, min(expires_days, 365))
    base_date = token.approved_at or datetime.utcnow()
    token.expires_days = expires_days
    token.expires_at = base_date + timedelta(days=expires_days)
    db.session.commit()
    return token, 'Validade atualizada com sucesso.'


def renew_user_token(user_id, expires_days=None):
    token = get_user_token(user_id)
    if not token or token.request_status != 'approved':
        return None, 'Você precisa ter um token aprovado para renovar.'

    now = datetime.utcnow()
    token.token = _generate_unique_token()
    token.expires_days = int(expires_days or token.expires_days or 30)
    token.expires_at = now + timedelta(days=token.expires_days)
    token.approved_at = now
    token.telegram_chat_id = None
    token.telegram_username = None
    db.session.commit()
    return token, 'Token renovado. Use /entrar no Telegram e cole o novo código.'


def logout_user_token(user_id):
    token = get_user_token(user_id)
    if not token:
        return False, 'Nenhum acesso do Telegram encontrado.'

    token.telegram_chat_id = None
    token.telegram_username = None
    db.session.commit()
    return True, 'Telegram desconectado. O token continua válido até a expiração.'


def validate_token(token_value, chat_id=None, telegram_username=None):
    token_value = (token_value or '').strip()
    token = TelegramToken.query.filter_by(token=token_value).first()
    if not token or not token.is_valid:
        return None, 'Token inválido, expirado ou ainda não aprovado.'

    if chat_id:
        existing = TelegramToken.query.filter(
            TelegramToken.telegram_chat_id == str(chat_id),
            TelegramToken.id != token.id
        ).first()
        if existing:
            existing.telegram_chat_id = None
            existing.telegram_username = None

        token.telegram_chat_id = str(chat_id)
        token.telegram_username = telegram_username
        db.session.commit()

    return token.user, 'Telegram conectado com sucesso.'


def get_user_by_chat_id(chat_id):
    token = TelegramToken.query.filter_by(telegram_chat_id=str(chat_id)).first()
    if not token or not token.is_valid:
        return None
    return User.query.filter_by(id=token.user_id, is_active=True, is_deleted=False).first()


def get_admin_tokens(status=None):
    query = TelegramToken.query.join(User).filter(User.is_deleted == False)
    if status in VALID_STATUSES:
        query = query.filter(TelegramToken.request_status == status)
    return query.order_by(TelegramToken.updated_at.desc()).all()


def get_admin_statistics():
    return {
        'pending': TelegramToken.query.filter_by(request_status='pending').count(),
        'approved': TelegramToken.query.filter_by(request_status='approved').count(),
        'connected': TelegramToken.query.filter(TelegramToken.telegram_chat_id.isnot(None)).count(),
        'expired': TelegramToken.query.filter(
            TelegramToken.request_status == 'approved',
            TelegramToken.expires_at <= datetime.utcnow()
        ).count()
    }
