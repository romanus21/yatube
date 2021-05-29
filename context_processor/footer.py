import datetime as dt


def year(request):
    current = dt.datetime.today().year
    return {
        'year' : current
    }
