import asyncio
import logging
import os
import threading

from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)
_bot_thread = None
_flask_app = None

STATE_WAITING_TOKEN = 'waiting_token'
STATE_AMOUNT = 'amount'
STATE_DESCRIPTION = 'description'


def _money(value):
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def _parse_amount(raw_value):
    value = raw_value.strip().replace('R$', '').replace(' ', '')
    if ',' in value and '.' in value:
        value = value.replace('.', '').replace(',', '.')
    elif ',' in value:
        value = value.replace(',', '.')
    return float(value)


def _main_menu_keyboard(InlineKeyboardButton, InlineKeyboardMarkup):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('➕ Nova transação', callback_data='new_transaction')],
        [InlineKeyboardButton('ℹ️ Ajuda', callback_data='help')],
    ])


async def _send_main_menu(update, context, text=None):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    message = text or (
        'Pronto. Estou conectado ao seu financeiro.\n\n'
        'Use os botões abaixo para registrar tudo sem atrito.'
    )
    keyboard = _main_menu_keyboard(InlineKeyboardButton, InlineKeyboardMarkup)

    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=keyboard)
    else:
        await update.message.reply_text(message, reply_markup=keyboard)


def _get_chat_user(chat_id):
    from services import telegram_service

    with _flask_app.app_context():
        return telegram_service.get_user_by_chat_id(chat_id)


async def entrar(update, context):
    user = _get_chat_user(update.effective_chat.id)
    if user:
        await _send_main_menu(
            update,
            context,
            f'Olá, {user.full_name or user.username}. Seu Telegram já está conectado.'
        )
        return

    context.user_data.clear()
    context.user_data['state'] = STATE_WAITING_TOKEN
    await update.message.reply_text(
        'Vamos conectar seu Telegram ao sistema financeiro.\n\n'
        'Cole aqui o token que aparece em Configurações > Telegram no sistema web.'
    )


async def sair(update, context):
    from services import telegram_service

    with _flask_app.app_context():
        user = telegram_service.get_user_by_chat_id(update.effective_chat.id)
        if user:
            telegram_service.logout_user_token(user.id)

    context.user_data.clear()
    await update.message.reply_text(
        'Telegram desconectado com sucesso.\n\n'
        'Quando quiser voltar, use /entrar e cole seu token.'
    )


async def cancelar(update, context):
    context.user_data.clear()
    await _send_main_menu(update, context, 'Operação cancelada. Pode começar de novo quando quiser.')


async def handle_text(update, context):
    from services import telegram_service, transaction_service

    chat_id = update.effective_chat.id
    state = context.user_data.get('state')

    if state == STATE_WAITING_TOKEN:
        token_value = update.message.text.strip()
        telegram_username = update.effective_user.username if update.effective_user else None
        with _flask_app.app_context():
            user, message = telegram_service.validate_token(token_value, chat_id, telegram_username)

        if not user:
            await update.message.reply_text(
                f'{message}\n\nConfira o token no sistema web e envie novamente, ou use /cancelar.'
            )
            return

        context.user_data.clear()
        await _send_main_menu(
            update,
            context,
            f'Conectado, {user.full_name or user.username}. Agora dá para registrar transações por aqui.'
        )
        return

    user = _get_chat_user(chat_id)
    if not user:
        await update.message.reply_text('Use /entrar para conectar seu Telegram antes de registrar transações.')
        return

    if state == STATE_AMOUNT:
        try:
            amount = _parse_amount(update.message.text)
        except ValueError:
            await update.message.reply_text('Digite um valor válido, por exemplo: 87,50 ou 1500.00')
            return

        if amount <= 0:
            await update.message.reply_text('O valor precisa ser maior que zero.')
            return

        context.user_data['amount'] = amount
        context.user_data['state'] = STATE_DESCRIPTION
        await update.message.reply_text('Agora me diga uma descrição curta. Exemplo: Almoço no shopping')
        return

    if state == STATE_DESCRIPTION:
        description = update.message.text.strip()
        if len(description) < 2:
            await update.message.reply_text('Escreva uma descrição um pouco mais clara para identificar depois.')
            return

        context.user_data['description'] = description[:200]
        await _show_confirmation(update, context)
        return

    await _send_main_menu(update, context, 'Estou por aqui. Escolha uma ação no menu.')


async def _show_confirmation(update, context):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from models import BankAccount, Category

    data = context.user_data
    with _flask_app.app_context():
        account = BankAccount.query.get(data.get('account_id'))
        category = Category.query.get(data.get('category_id'))

    transaction_label = 'Receita' if data.get('type') == 'receita' else 'Despesa'
    text = (
        f'Confira antes de salvar:\n\n'
        f'Tipo: {transaction_label}\n'
        f'Conta: {account.name if account else "-"}\n'
        f'Categoria: {category.name if category else "-"}\n'
        f'Valor: {_money(data.get("amount", 0))}\n'
        f'Descrição: {data.get("description")}'
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('✅ Confirmar', callback_data='confirm_transaction')],
        [InlineKeyboardButton('❌ Cancelar', callback_data='cancel_flow')],
    ])
    await update.message.reply_text(text, reply_markup=keyboard)


async def handle_callback(update, context):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from services import account_service, category_service, transaction_service

    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    action = query.data

    if action == 'help':
        keyboard = _main_menu_keyboard(InlineKeyboardButton, InlineKeyboardMarkup)
        await query.edit_message_text(
            'Comandos úteis:\n\n'
            '/entrar - conectar seu Telegram\n'
            '/sair - desconectar este chat\n'
            '/cancelar - cancelar uma operação\n\n'
            'Para lançar uma transação, toque em Nova transação e siga o passo a passo.',
            reply_markup=keyboard
        )
        return

    if action == 'cancel_flow':
        context.user_data.clear()
        await _send_main_menu(update, context, 'Lançamento cancelado. Nada foi salvo.')
        return

    user = _get_chat_user(chat_id)
    if not user:
        await query.edit_message_text('Use /entrar para conectar seu Telegram antes de continuar.')
        return

    if action == 'new_transaction':
        context.user_data.clear()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('💰 Receita', callback_data='type:receita')],
            [InlineKeyboardButton('💸 Despesa', callback_data='type:despesa')],
        ])
        await query.edit_message_text('Qual tipo de transação você quer registrar?', reply_markup=keyboard)
        return

    if action.startswith('type:'):
        transaction_type = action.split(':', 1)[1]
        context.user_data['type'] = transaction_type

        with _flask_app.app_context():
            accounts = account_service.get_user_accounts(user.id)

        if not accounts:
            await query.edit_message_text('Você ainda não tem contas bancárias cadastradas no sistema web.')
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f'{account.name} - {_money(account.balance)}', callback_data=f'account:{account.id}')]
            for account in accounts
        ])
        await query.edit_message_text('Escolha a conta bancária:', reply_markup=keyboard)
        return

    if action.startswith('account:'):
        account_id = int(action.split(':', 1)[1])
        context.user_data['account_id'] = account_id

        with _flask_app.app_context():
            categories = category_service.get_user_categories(user.id, context.user_data.get('type'), True)

        if not categories:
            await query.edit_message_text('Você ainda não tem categorias ativas para esse tipo de transação.')
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(category.name, callback_data=f'category:{category.id}')]
            for category in categories
        ])
        await query.edit_message_text('Agora escolha a categoria:', reply_markup=keyboard)
        return

    if action.startswith('category:'):
        category_id = int(action.split(':', 1)[1])
        context.user_data['category_id'] = category_id
        context.user_data['state'] = STATE_AMOUNT
        await query.edit_message_text('Digite o valor em R$. Exemplo: 87,50')
        return

    if action == 'confirm_transaction':
        data = context.user_data
        required = ('type', 'account_id', 'category_id', 'amount', 'description')
        if not all(key in data for key in required):
            context.user_data.clear()
            await _send_main_menu(update, context, 'Não encontrei todos os dados do lançamento. Vamos começar de novo.')
            return

        with _flask_app.app_context():
            transaction, message = transaction_service.create_transaction(
                user.id,
                data['account_id'],
                data['category_id'],
                data['type'],
                data['amount'],
                data['description'],
                True,
                user.is_mei
            )

        if not transaction:
            await query.edit_message_text(f'Não consegui salvar: {message}')
            return

        saved_type = 'Receita' if data['type'] == 'receita' else 'Despesa'
        amount = data['amount']
        description = data['description']
        context.user_data.clear()
        await _send_main_menu(
            update,
            context,
            f'Transação registrada.\n\n{saved_type}: {_money(amount)}\nDescrição: {description}'
        )


def _run_bot(token, flask_app):
    global _flask_app
    _flask_app = flask_app

    from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler(['start', 'entrar'], entrar))
    application.add_handler(CommandHandler('sair', sair))
    application.add_handler(CommandHandler('cancelar', cancelar))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info('Bot Telegram iniciado.')
    application.run_polling(drop_pending_updates=True, close_loop=False, stop_signals=None)


def start_telegram_bot(flask_app):
    global _bot_thread

    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.info('TELEGRAM_BOT_TOKEN não configurado. Bot Telegram não iniciado.')
        return None

    if _bot_thread and _bot_thread.is_alive():
        return _bot_thread

    try:
        import telegram  # noqa: F401
    except ImportError:
        logger.warning('python-telegram-bot não instalado. Execute pip install -r requirements.txt.')
        return None

    _bot_thread = threading.Thread(target=_run_bot, args=(token, flask_app), daemon=True)
    _bot_thread.start()
    print('🤖 Bot Telegram iniciado com sucesso!')
    return _bot_thread
