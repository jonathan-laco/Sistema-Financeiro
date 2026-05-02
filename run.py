from app import app
from seed import run_seed
from telegram_bot import start_telegram_bot
import os

if __name__ == '__main__':
    with app.app_context():
        try:
            run_seed()
        except Exception as e:
            print(f"Erro ao executar seed: {e}")
            print("Continuando a execução da aplicação...")

    debug = True
    should_start_bot = not debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    if should_start_bot:
        start_telegram_bot(app)

    app.run(debug=debug, host='0.0.0.0', port=5000)
