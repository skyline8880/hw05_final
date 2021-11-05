import datetime as dt


date = dt.date.today().year


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': date
    }
