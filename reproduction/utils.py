import ephem


def get_lunar_phase(date_obj):
    """Retorna o nome da fase da lua para uma determinada data."""
    date_str = date_obj.strftime("%Y/%m/%d")
    date_ephem = ephem.Date(date_str)

    # Próximas fases da lua a partir da data informada
    next_new = ephem.next_new_moon(date_ephem)
    next_first_quarter = ephem.next_first_quarter_moon(date_ephem)
    next_full = ephem.next_full_moon(date_ephem)
    next_last_quarter = ephem.next_last_quarter_moon(date_ephem)

    # Descobre qual fase está mais próxima
    phases = [
        ('Nova', next_new),
        ('Crescente', next_first_quarter),
        ('Cheia', next_full),
        ('Minguante', next_last_quarter)
    ]
    phases.sort(key=lambda x: abs(x[1] - date_ephem))
    return phases[0][0]