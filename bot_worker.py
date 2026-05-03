"""Processo dedicado para executar o bot do Telegram.

Use este arquivo quando a aplicacao Flask estiver rodando via Gunicorn/Waitress
ou outro servidor WSGI. O servidor web e o bot devem ser processos separados.
"""

import logging
import signal
import sys
import time

from app import app
from telegram_bot import start_telegram_bot


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s]: %(message)s',
)
logger = logging.getLogger(__name__)
_should_stop = False


def _handle_stop(signum, frame):
    global _should_stop
    _should_stop = True
    logger.info('Sinal %s recebido. Encerrando bot worker...', signum)


def main():
    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)

    bot_thread = start_telegram_bot(app)
    if not bot_thread:
        logger.error('Bot Telegram nao foi iniciado. Confira TELEGRAM_BOT_TOKEN e dependencias.')
        return 1

    logger.info('Bot worker iniciado. Mantenha apenas uma instancia deste processo rodando.')

    while not _should_stop:
        if not bot_thread.is_alive():
            logger.error('Thread do bot Telegram parou inesperadamente.')
            return 1
        time.sleep(2)

    logger.info('Bot worker encerrado.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
