def parse_brl_number(value, default=None):
    if value is None or value == '':
        if default is not None:
            return default
        raise ValueError('Valor numerico vazio')

    if isinstance(value, (int, float)):
        return float(value)

    normalized = str(value).strip().replace('R$', '').replace(' ', '')

    if ',' in normalized:
        normalized = normalized.replace('.', '').replace(',', '.')
    elif normalized.count('.') > 1:
        normalized = normalized.replace('.', '')

    return float(normalized)


def format_number(value, decimal_places=2):
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        number = 0

    formatted = f'{number:,.{decimal_places}f}'
    return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')


def format_brl(value):
    return f'R$ {format_number(value)}'


def format_brl_input(value):
    return format_number(value)
