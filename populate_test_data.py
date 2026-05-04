import calendar
import os
import random
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import List, Optional
from urllib.parse import unquote


PROJECT_ROOT = Path(__file__).resolve().parent
DATABASE_CANDIDATES = [
    PROJECT_ROOT / "instance" / "finance.db",
    PROJECT_ROOT / "finance.db",
    Path.cwd() / "instance" / "finance.db",
    Path.cwd() / "finance.db",
]
DEFAULT_YEAR = 2026
MARKER = "[POPTEST]"


INCOME_TEMPLATES = {
    "Salário": [("Salário mensal", 3200, 9200), ("Adiantamento salarial", 800, 2400)],
    "Investimentos": [("Dividendos recebidos", 40, 900), ("Rendimento investimento", 25, 650)],
    "Freelance": [("Projeto freelance", 350, 4500), ("Consultoria pontual", 250, 2800)],
    "Presente": [("Presente recebido", 50, 700), ("Ajuda familiar", 80, 1100)],
    "Outros": [("Receita extra", 40, 1300), ("Venda de item usado", 70, 1800)],
}

EXPENSE_TEMPLATES = {
    "Alimentação": [("Supermercado", 45, 620), ("Padaria", 12, 85), ("Restaurante", 35, 190)],
    "Moradia": [("Aluguel", 900, 3200), ("Condomínio", 180, 850), ("Conta de luz", 90, 420)],
    "Transporte": [("Combustível", 80, 360), ("Aplicativo de transporte", 18, 130), ("Ônibus/metrô", 5, 70)],
    "Saúde": [("Farmácia", 25, 260), ("Consulta médica", 120, 550), ("Plano de saúde", 180, 780)],
    "Educação": [("Curso online", 50, 450), ("Material de estudo", 25, 220)],
    "Lazer": [("Cinema", 35, 160), ("Streaming", 19, 75), ("Passeio", 40, 260)],
    "Outros": [("Compra avulsa", 20, 300), ("Manutenção", 60, 650)],
}

DEFAULT_ACCOUNTS = [
    ("Conta Corrente Teste", 1200.00),
    ("Cartão/Carteira Teste", 350.00),
    ("Reserva Teste", 2500.00),
]

DEFAULT_INCOME_CATEGORIES = [
    ("Salário", "#28a745"),
    ("Investimentos", "#20c997"),
    ("Freelance", "#17a2b8"),
    ("Presente", "#ffc107"),
    ("Outros", "#6c757d"),
]

DEFAULT_EXPENSE_CATEGORIES = [
    ("Alimentação", "#dc3545"),
    ("Moradia", "#e83e8c"),
    ("Transporte", "#fd7e14"),
    ("Saúde", "#6f42c1"),
    ("Educação", "#0275d8"),
    ("Lazer", "#4169e1"),
    ("Outros", "#6c757d"),
]


@dataclass
class Config:
    user_id: int
    year: int
    months: List[int]
    transactions_per_month: int
    confirmed_rate: float
    pending_rate: float
    include_mei: bool
    mei_rate: float
    include_support_months: bool
    clear_previous: bool
    seed: Optional[int]


def ask(prompt, default=None):
    suffix = f" [{default}]" if default not in (None, "") else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value if value else default


def ask_int(prompt, default, minimum=None, maximum=None):
    while True:
        value = ask(prompt, default)
        try:
            number = int(value)
        except (TypeError, ValueError):
            print("Informe um número inteiro válido.")
            continue
        if minimum is not None and number < minimum:
            print(f"O valor mínimo é {minimum}.")
            continue
        if maximum is not None and number > maximum:
            print(f"O valor máximo é {maximum}.")
            continue
        return number


def ask_float(prompt, default, minimum=None, maximum=None):
    while True:
        value = str(ask(prompt, default)).replace(",", ".")
        try:
            number = float(value)
        except (TypeError, ValueError):
            print("Informe um número válido.")
            continue
        if minimum is not None and number < minimum:
            print(f"O valor mínimo é {minimum}.")
            continue
        if maximum is not None and number > maximum:
            print(f"O valor máximo é {maximum}.")
            continue
        return number


def ask_yes_no(prompt, default=True):
    default_text = "s" if default else "n"
    while True:
        value = str(ask(f"{prompt} (s/n)", default_text)).lower()
        if value in ("s", "sim", "y", "yes"):
            return True
        if value in ("n", "nao", "não", "no"):
            return False
        print("Responda com s ou n.")


def parse_months(raw):
    if not raw or str(raw).lower() in ("todos", "todas", "all", "*"):
        return list(range(1, 13))

    months = set()
    for part in str(raw).replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            months.update(range(int(start), int(end) + 1))
        else:
            months.add(int(part))

    invalid = [m for m in months if m < 1 or m > 12]
    if invalid:
        raise ValueError("Meses devem ficar entre 1 e 12.")
    return sorted(months)


def table_columns(cursor, table):
    cursor.execute(f'PRAGMA table_info("{table}")')
    return {row["name"] for row in cursor.fetchall()}


def sqlite_path_from_database_url(database_url):
    if not database_url or not database_url.startswith("sqlite"):
        return None

    for prefix in ("sqlite+pysqlite:///", "sqlite:///"):
        if not database_url.startswith(prefix):
            continue
        raw_path = unquote(database_url[len(prefix):])
        if not raw_path:
            return None
        if raw_path.startswith("/") or (len(raw_path) > 2 and raw_path[1] == ":"):
            return Path(raw_path)
        return PROJECT_ROOT / raw_path

    if database_url.startswith("sqlite://"):
        return None
    return None


def resolve_database_path():
    env_path = sqlite_path_from_database_url(os.environ.get("DATABASE_URL"))
    candidates = [env_path] if env_path else []
    candidates.extend(DATABASE_CANDIDATES)

    for path in candidates:
        if path and path.exists():
            return path.resolve()

    print("\nNão encontrei o banco SQLite automaticamente.")
    print("Locais testados:")
    for path in candidates:
        if path:
            print(f"- {path}")

    while True:
        raw_path = ask("Informe o caminho do arquivo .db", str(PROJECT_ROOT / "instance" / "finance.db"))
        path = Path(raw_path).expanduser()
        if path.exists():
            return path.resolve()
        print("Arquivo não encontrado. Confira o caminho e tente de novo.")


def connect():
    database_path = resolve_database_path()
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn, database_path


def list_users(cursor):
    columns = table_columns(cursor, "user")
    filters = []
    if "is_deleted" in columns:
        filters.append("(is_deleted = 0 OR is_deleted IS NULL)")
    if "is_active" in columns:
        filters.append("(is_active = 1 OR is_active IS NULL)")

    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    cursor.execute(
        f"""
        SELECT id, username, email, full_name, is_admin, is_mei
        FROM user
        {where}
        ORDER BY is_admin ASC, id ASC
        """
    )
    return cursor.fetchall()


def choose_user(cursor):
    users = list_users(cursor)
    if not users:
        raise SystemExit("Nenhum usuário ativo encontrado.")

    print("\nUsuários disponíveis:")
    for idx, user in enumerate(users, start=1):
        tags = []
        if user["is_admin"]:
            tags.append("admin")
        if user["is_mei"]:
            tags.append("MEI")
        tag_text = f" ({', '.join(tags)})" if tags else ""
        name = user["full_name"] or user["username"]
        print(f"{idx}. ID {user['id']} - {name} <{user['email']}>{tag_text}")

    while True:
        choice = ask_int("\nSelecione o usuário pelo número da lista", 1, 1, len(users))
        selected = users[choice - 1]
        if selected["is_admin"]:
            if not ask_yes_no("Você selecionou um admin. Deseja continuar mesmo assim?", False):
                continue
        return selected


def ensure_accounts(cursor, conn, user_id):
    cursor.execute(
        """
        SELECT id, name, balance
        FROM bank_account
        WHERE user_id = ? AND (is_deleted = 0 OR is_deleted IS NULL)
        ORDER BY id
        """,
        (user_id,),
    )
    accounts = cursor.fetchall()
    if accounts:
        return accounts

    if not ask_yes_no("Nenhuma conta ativa encontrada. Criar contas de teste?", True):
        raise SystemExit("Crie ao menos uma conta para gerar transações.")

    cursor.executemany(
        "INSERT INTO bank_account (user_id, name, balance, is_deleted) VALUES (?, ?, ?, 0)",
        [(user_id, name, balance) for name, balance in DEFAULT_ACCOUNTS],
    )
    conn.commit()
    cursor.execute(
        """
        SELECT id, name, balance
        FROM bank_account
        WHERE user_id = ? AND (is_deleted = 0 OR is_deleted IS NULL)
        ORDER BY id
        """,
        (user_id,),
    )
    return cursor.fetchall()


def ensure_categories(cursor, conn, user_id):
    cursor.execute(
        """
        SELECT id, name, type, color
        FROM category
        WHERE user_id = ? AND is_active = 1
        ORDER BY type, name
        """,
        (user_id,),
    )
    categories = cursor.fetchall()
    has_income = any(category["type"] == "receita" for category in categories)
    has_expense = any(category["type"] == "despesa" for category in categories)
    if has_income and has_expense:
        return categories

    if not ask_yes_no("Categorias ativas insuficientes. Criar categorias padrão?", True):
        raise SystemExit("São necessárias categorias ativas de receita e despesa.")

    existing = {(category["name"], category["type"]) for category in categories}
    inserts = []
    for name, color in DEFAULT_INCOME_CATEGORIES:
        if (name, "receita") not in existing:
            inserts.append((user_id, name, "receita", 1, color))
    for name, color in DEFAULT_EXPENSE_CATEGORIES:
        if (name, "despesa") not in existing:
            inserts.append((user_id, name, "despesa", 1, color))

    cursor.executemany(
        "INSERT INTO category (user_id, name, type, is_active, color) VALUES (?, ?, ?, ?, ?)",
        inserts,
    )
    conn.commit()
    cursor.execute(
        """
        SELECT id, name, type, color
        FROM category
        WHERE user_id = ? AND is_active = 1
        ORDER BY type, name
        """,
        (user_id,),
    )
    return cursor.fetchall()


def ask_config(selected_user):
    print("\nConfiguração da massa de dados")
    year = ask_int("Ano para popular", DEFAULT_YEAR, 2000, 2100)

    while True:
        raw_months = ask("Meses (ex: todos, 1-12, 1,2,5)", "todos")
        try:
            months = parse_months(raw_months)
            break
        except ValueError as exc:
            print(exc)

    transactions_per_month = ask_int("Transações por mês", 80, 1, 2000)
    confirmed_rate = ask_float("% confirmadas para entrar nos gráficos/relatórios", 88, 0, 100) / 100
    pending_rate = ask_float("% pendentes para testar painel de pendências", 9, 0, 100) / 100
    if confirmed_rate + pending_rate > 1:
        print("A soma de confirmadas e pendentes passou de 100%; ajustando pendentes.")
        pending_rate = max(0, 1 - confirmed_rate)

    include_mei_default = bool(selected_user["is_mei"])
    include_mei = ask_yes_no("Marcar parte das transações como MEI?", include_mei_default)
    mei_rate = 0
    if include_mei:
        mei_rate = ask_float("% das transações como MEI", 65 if include_mei_default else 25, 0, 100) / 100

    include_support_months = ask_yes_no(
        "Popular meses de apoio para o dashboard dos últimos 6 meses, se necessário?",
        True,
    )
    clear_previous = ask_yes_no(
        f"Apagar dados de teste anteriores ({MARKER}) desse usuário/ano antes de inserir?",
        True,
    )
    seed = ask_seed()

    return Config(
        user_id=selected_user["id"],
        year=year,
        months=months,
        transactions_per_month=transactions_per_month,
        confirmed_rate=confirmed_rate,
        pending_rate=pending_rate,
        include_mei=include_mei,
        mei_rate=mei_rate,
        include_support_months=include_support_months,
        clear_previous=clear_previous,
        seed=seed,
    )


def ask_seed():
    empty_values = {"", "vazio", "aleatorio", "aleatório", "random", "none", "n", "nao", "não"}
    while True:
        seed_raw = str(ask("Seed numérica para repetir o mesmo cenário (Enter/vazio = aleatório)", "")).strip()
        if seed_raw.lower() in empty_values:
            return None
        try:
            return int(seed_raw)
        except ValueError:
            print("Informe um número inteiro para repetir o cenário, ou deixe vazio para usar aleatório.")


def support_year_months(config):
    selected = {(config.year, month) for month in config.months}
    if not config.include_support_months:
        return sorted(selected)

    today = date.today()
    if config.year != today.year:
        return sorted(selected)

    for offset in range(6):
        month = today.month - offset
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        selected.add((year, month))
    return sorted(selected)


def weighted_choice(items, weight_by_name):
    weighted = []
    for item in items:
        weight = weight_by_name.get(item["name"], 1)
        weighted.append((item, weight))
    total = sum(weight for _, weight in weighted)
    marker = random.uniform(0, total)
    current = 0
    for item, weight in weighted:
        current += weight
        if marker <= current:
            return item
    return weighted[-1][0]


def pick_template(category, templates):
    options = templates.get(category["name"]) or templates.get("Outros")
    description, low, high = random.choice(options)
    amount = random.uniform(low, high)
    return description, round(amount, 2)


def random_datetime(year, month, recurring_day=None):
    last_day = calendar.monthrange(year, month)[1]
    day = recurring_day or random.randint(1, last_day)
    day = min(day, last_day)
    hour = random.randint(7, 22)
    minute = random.choice([0, 5, 10, 15, 20, 30, 40, 45, 50])
    return datetime.combine(date(year, month, day), time(hour, minute))


def status_for(config):
    roll = random.random()
    if roll < config.confirmed_rate:
        return "confirmado", 1
    if roll < config.confirmed_rate + config.pending_rate:
        return "pendente", 0
    return "cancelado", 0


def generate_month_transactions(config, accounts, income_categories, expense_categories, year, month):
    transactions = []
    income_weights = {"Salário": 8, "Freelance": 4, "Investimentos": 3, "Outros": 2, "Presente": 1}
    expense_weights = {
        "Alimentação": 8,
        "Transporte": 6,
        "Moradia": 5,
        "Lazer": 4,
        "Saúde": 3,
        "Educação": 2,
        "Outros": 2,
    }

    fixed_expenses = ["Moradia", "Saúde", "Educação"]
    if any(cat["name"] == "Salário" for cat in income_categories):
        salary_category = next(cat for cat in income_categories if cat["name"] == "Salário")
        account = random.choice(accounts)
        status, is_confirmed = status_for(config)
        description, amount = pick_template(salary_category, INCOME_TEMPLATES)
        transactions.append(build_row(config, account, salary_category, "receita", amount, description, year, month, 5, status, is_confirmed))

    for fixed_name in fixed_expenses:
        category = next((cat for cat in expense_categories if cat["name"] == fixed_name), None)
        if not category:
            continue
        account = random.choice(accounts)
        status, is_confirmed = status_for(config)
        description, amount = pick_template(category, EXPENSE_TEMPLATES)
        transactions.append(build_row(config, account, category, "despesa", amount, description, year, month, random.choice([8, 10, 15]), status, is_confirmed))

    variable_count = max(0, config.transactions_per_month - len(transactions))
    for _ in range(variable_count):
        transaction_type = "despesa" if random.random() < 0.72 else "receita"
        account = random.choice(accounts)
        status, is_confirmed = status_for(config)
        if transaction_type == "receita":
            category = weighted_choice(income_categories, income_weights)
            description, amount = pick_template(category, INCOME_TEMPLATES)
        else:
            category = weighted_choice(expense_categories, expense_weights)
            description, amount = pick_template(category, EXPENSE_TEMPLATES)

        transactions.append(
            build_row(config, account, category, transaction_type, amount, description, year, month, None, status, is_confirmed)
        )

    return transactions


def build_row(config, account, category, transaction_type, amount, description, year, month, day, status, is_confirmed):
    dt = random_datetime(year, month, day)
    is_mei = 1 if config.include_mei and random.random() < config.mei_rate else 0
    has_invoice = 1 if is_mei and transaction_type == "receita" and random.random() < 0.55 else 0
    final_description = f"{MARKER} {description} - {category['name']}"
    return (
        config.user_id,
        account["id"],
        category["id"],
        transaction_type,
        amount,
        final_description,
        dt.strftime("%Y-%m-%d %H:%M:%S"),
        is_confirmed,
        status,
        is_mei,
        has_invoice,
        0,
    )


def delete_previous(cursor, config, year_months):
    deleted_effects = {}
    for year, month in year_months:
        start = f"{year:04d}-{month:02d}-01 00:00:00"
        last_day = calendar.monthrange(year, month)[1]
        end = f"{year:04d}-{month:02d}-{last_day:02d} 23:59:59"
        cursor.execute(
            """
            SELECT account_id, type, SUM(amount) AS amount
            FROM "transaction"
            WHERE user_id = ?
              AND description LIKE ?
              AND status = 'confirmado'
              AND (is_deleted = 0 OR is_deleted IS NULL)
              AND date BETWEEN ? AND ?
            GROUP BY account_id, type
            """,
            (config.user_id, f"{MARKER}%", start, end),
        )
        for row in cursor.fetchall():
            effect = row["amount"] if row["type"] == "receita" else -row["amount"]
            deleted_effects[row["account_id"]] = deleted_effects.get(row["account_id"], 0) + effect

        cursor.execute(
            """
            DELETE FROM "transaction"
            WHERE user_id = ?
              AND description LIKE ?
              AND date BETWEEN ? AND ?
            """,
            (config.user_id, f"{MARKER}%", start, end),
        )
    return deleted_effects


def insert_transactions(cursor, rows):
    cursor.executemany(
        """
        INSERT INTO "transaction"
        (
            user_id, account_id, category_id, type, amount, description, date,
            is_confirmed, status, is_mei_transaction, has_invoice, is_deleted
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )


def inserted_balance_effects(rows):
    effects = {}
    for row in rows:
        account_id = row[1]
        transaction_type = row[3]
        amount = row[4]
        status = row[8]
        if status != "confirmado":
            continue
        effect = amount if transaction_type == "receita" else -amount
        effects[account_id] = effects.get(account_id, 0) + effect
    return effects


def apply_balance_effects(cursor, deleted_effects, inserted_effects):
    account_ids = set(deleted_effects) | set(inserted_effects)
    for account_id in account_ids:
        balance_delta = inserted_effects.get(account_id, 0) - deleted_effects.get(account_id, 0)
        cursor.execute(
            "UPDATE bank_account SET balance = ROUND(balance + ?, 2) WHERE id = ?",
            (round(balance_delta, 2), account_id),
        )


def print_summary(cursor, config, inserted, year_months):
    cursor.execute(
        """
        SELECT status, type, COUNT(*) AS total, ROUND(SUM(amount), 2) AS amount
        FROM "transaction"
        WHERE user_id = ?
          AND description LIKE ?
          AND is_deleted = 0
        GROUP BY status, type
        ORDER BY status, type
        """,
        (config.user_id, f"{MARKER}%"),
    )
    rows = cursor.fetchall()

    print("\nResumo da massa gerada")
    print(f"- Usuário ID: {config.user_id}")
    print(f"- Ano base: {config.year}")
    print(f"- Meses populados: {', '.join(f'{y}-{m:02d}' for y, m in year_months)}")
    print(f"- Novas transações inseridas: {inserted}")
    print("- Marcador nas descrições:", MARKER)
    print("\nTotais por status/tipo:")
    for row in rows:
        print(f"  {row['status']:<10} {row['type']:<8} {row['total']:>5} transações | R$ {row['amount'] or 0:.2f}")

    cursor.execute(
        """
        SELECT name, ROUND(balance, 2) AS balance
        FROM bank_account
        WHERE user_id = ? AND (is_deleted = 0 OR is_deleted IS NULL)
        ORDER BY name
        """,
        (config.user_id,),
    )
    print("\nSaldos atuais:")
    for account in cursor.fetchall():
        print(f"  {account['name']}: R$ {account['balance']:.2f}")


def main():
    print("Popular dados de teste do Sistema Financeiro")

    conn, database_path = connect()
    print(f"Banco: {database_path}")
    cursor = conn.cursor()

    try:
        selected_user = choose_user(cursor)
        accounts = ensure_accounts(cursor, conn, selected_user["id"])
        categories = ensure_categories(cursor, conn, selected_user["id"])
        config = ask_config(selected_user)

        if config.seed is not None:
            random.seed(config.seed)

        income_categories = [cat for cat in categories if cat["type"] == "receita"]
        expense_categories = [cat for cat in categories if cat["type"] == "despesa"]
        year_months = support_year_months(config)

        deleted_effects = {}
        if config.clear_previous:
            deleted_effects = delete_previous(cursor, config, year_months)

        rows = []
        for year, month in year_months:
            month_config = config
            if year != config.year:
                month_config = Config(**{**config.__dict__, "transactions_per_month": max(25, config.transactions_per_month // 2)})
            rows.extend(generate_month_transactions(month_config, accounts, income_categories, expense_categories, year, month))

        insert_transactions(cursor, rows)
        apply_balance_effects(cursor, deleted_effects, inserted_balance_effects(rows))
        conn.commit()
        print_summary(cursor, config, len(rows), year_months)
        print("\nPronto. Os dados confirmados já alimentam dashboard, gráficos mensais, gráficos anuais e relatórios.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
