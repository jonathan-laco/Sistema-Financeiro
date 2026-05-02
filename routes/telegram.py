from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from services import telegram_service


telegram_bp = Blueprint('telegram', __name__, url_prefix='/telegram')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acesso negado. Você precisa ser administrador.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@telegram_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for('telegram.admin_tokens'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'request_access':
            _, message = telegram_service.request_access(current_user.id)
            flash(message, 'success')
        elif action == 'renew':
            token, message = telegram_service.renew_user_token(current_user.id)
            flash(message, 'success' if token else 'warning')
        elif action == 'logout':
            success, message = telegram_service.logout_user_token(current_user.id)
            flash(message, 'success' if success else 'warning')
        else:
            flash('Ação inválida.', 'danger')

        return redirect(url_for('telegram.index'))

    token = telegram_service.get_or_create_user_token(current_user.id)
    return render_template('telegram.html', telegram_token=token)


@telegram_bp.route('/admin', methods=['GET'])
@login_required
@admin_required
def admin_tokens():
    status = request.args.get('status')
    tokens = telegram_service.get_admin_tokens(status)
    stats = telegram_service.get_admin_statistics()
    return render_template('admin/telegram_tokens.html', tokens=tokens, stats=stats, active_status=status)


@telegram_bp.route('/admin/<int:token_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve(token_id):
    expires_days = request.form.get('expires_days', 30)
    admin_note = request.form.get('admin_note')
    token, message = telegram_service.approve_request(token_id, expires_days, admin_note)
    flash(message, 'success' if token else 'danger')
    return redirect(url_for('telegram.admin_tokens'))


@telegram_bp.route('/admin/<int:token_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject(token_id):
    admin_note = request.form.get('admin_note')
    token, message = telegram_service.reject_request(token_id, admin_note)
    flash(message, 'success' if token else 'danger')
    return redirect(url_for('telegram.admin_tokens'))


@telegram_bp.route('/admin/<int:token_id>/disable', methods=['POST'])
@login_required
@admin_required
def disable(token_id):
    admin_note = request.form.get('admin_note')
    token, message = telegram_service.disable_token(token_id, admin_note)
    flash(message, 'success' if token else 'danger')
    return redirect(url_for('telegram.admin_tokens'))


@telegram_bp.route('/admin/<int:token_id>/expiration', methods=['POST'])
@login_required
@admin_required
def update_expiration(token_id):
    expires_days = request.form.get('expires_days')
    token, message = telegram_service.update_expiration(token_id, expires_days)
    flash(message, 'success' if token else 'danger')
    return redirect(url_for('telegram.admin_tokens'))
