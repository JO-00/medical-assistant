from datetime import datetime, date

def _number_to_french(n):
    """Convert number to French words (0-31 and 45)"""
    french_numbers = {
        0: 'zéro', 1: 'un', 2: 'deux', 3: 'trois', 4: 'quatre',
        5: 'cinq', 6: 'six', 7: 'sept', 8: 'huit', 9: 'neuf',
        10: 'dix', 11: 'onze', 12: 'douze', 13: 'treize',
        14: 'quatorze', 15: 'quinze', 16: 'seize',
        17: 'dix-sept', 18: 'dix-huit', 19: 'dix-neuf', 20: 'vingt',
        21: 'vingt et un', 22: 'vingt-deux', 23: 'vingt-trois',
        24: 'vingt-quatre', 25: 'vingt-cinq', 26: 'vingt-six',
        27: 'vingt-sept', 28: 'vingt-huit', 29: 'vingt-neuf',
        30: 'trente', 31: 'trente et un',
        45: 'quarante-cinq'
    }
    return french_numbers.get(n, str(n))

def _format_date_french(value):
    """Format date in a TTS-friendly French way"""
    months = {
        1: 'janvier', 2: 'février', 3: 'mars',
        4: 'avril', 5: 'mai', 6: 'juin',
        7: 'juillet', 8: 'août', 9: 'septembre',
        10: 'octobre', 11: 'novembre', 12: 'décembre'
    }
    
    # If it's already a datetime/date object
    if isinstance(value, (datetime, date)):
        day = value.day
        month = months[value.month]
        year = value.year
        day_words = _number_to_french(day)
        
        # If it's a datetime with time, include the time
        if isinstance(value, datetime):
            hour = value.hour
            minute = value.minute
            time_str = f"{_number_to_french(hour)} heures {_number_to_french(minute)} minutes"
            return f"{day_words} {month} {year} à {time_str}"
        else:
            return f"{day_words} {month} {year}"
    
    # If it's a string, try to parse it
    if isinstance(value, str):
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(value, fmt)
                day = dt.day
                month = months[dt.month]
                year = dt.year
                day_words = _number_to_french(day)
                
                if ' ' in value or 'T' in value:
                    time_str = f"{_number_to_french(dt.hour)} heures {_number_to_french(dt.minute)} minutes"
                    return f"{day_words} {month} {year} à {time_str}"
                else:
                    return f"{day_words} {month} {year}"
            except ValueError:
                continue
    
    return str(value)

def _format_rows(rows, table_name: str):
    """Format query results as a friendly French paragraph for TTS"""
    if not rows:
        return "Aucun résultat trouvé dans la base de données."
    
    table_configs = {
        'patient': {
            'columns': ['nom', 'prenom', 'date_naissance', 'email'],
            'display_names': {
                'nom': 'nom',
                'prenom': 'prénom',
                'date_naissance': 'date de naissance',
                'email': 'adresse mail'
            },
            'item_name': 'patient',
            'display_name': 'patients'
        },
        'rdv': {
            'columns': ['date_rdv', 'duree', 'motif', 'etat'],
            'display_names': {
                'date_rdv': 'date du rendez-vous',
                'duree': 'durée en minutes',
                'motif': 'motif',
                'etat': 'état'
            },
            'item_name': 'rendez-vous',
            'display_name': 'rendez-vous'
        },
        'note_patient': {
            'columns': ['id_patient', 'note_medecin'],
            'display_names': {
                'id_patient': 'identifiant du patient',
                'note_medecin': 'note'
            },
            'item_name': 'note',
            'display_name': 'notes de vos patients'
        },
        'acte_medecin': {
            'columns': ['acte', 'duree', 'prix'],
            'display_names': {
                'acte': 'acte médical',
                'duree': 'durée en minutes',
                'prix': 'prix en dinars'
            },
            'item_name': 'acte médical',
            'display_name': 'actes médicaux'
        }
    }
    
    # Validate table_name exists in configs
    assert table_name in table_configs, f"Table '{table_name}' not found in table_configs"
    
    config = table_configs[table_name]
    columns = config['columns']
    display_names = config['display_names']
    item_name = config['item_name']
    display_name = config['display_name']
    row_count = len(rows)
    
    # Build the response
    parts = []
    
    # French number words up to 5
    number_words = ["un", "deux", "trois", "quatre", "cinq"]
    
    # Introduction based on count - limit to 5
    if row_count == 1:
        if table_name == 'rdv':
            parts.append(f"J'ai trouvé un de vos {display_name}.")
        elif table_name == 'patient':
            parts.append(f"J'ai trouvé un de vos {display_name}.")
        else:
            parts.append(f"J'ai trouvé un {item_name}.")
    else:
        # Only show count up to 5, then just say "plusieurs"
        if row_count <= 5:
            if table_name == 'rdv':
                parts.append(f"J'ai trouvé {number_words[row_count-1]} de vos {display_name}.")
            elif table_name == 'patient':
                parts.append(f"J'ai trouvé {number_words[row_count-1]} de vos {display_name}.")
            else:
                parts.append(f"J'ai trouvé {number_words[row_count-1]} {display_name}.")
        else:
            if table_name == 'rdv':
                parts.append(f"J'ai trouvé plusieurs de vos {display_name}.")
            elif table_name == 'patient':
                parts.append(f"J'ai trouvé plusieurs de vos {display_name}.")
            elif table_name == 'note_patient':
                parts.append(f"J'ai trouvé plusieurs {display_name}.")
            else:
                parts.append(f"J'ai trouvé plusieurs {display_name}.")
    
    parts.append("")
    
    # Limit to 5 elements
    display_rows = rows[:5]
    has_more = row_count > 5
    
    # Format each row (max 5)
    for idx, row in enumerate(display_rows, 1):
        # Skip rows with no data
        if not row:
            continue
            
        # Ordinals in French
        ordinals = ["Premier", "Deuxième", "Troisième", "Quatrième", "Cinquième"]
        item_intro = f"{ordinals[idx-1]} élément :"
        parts.append(item_intro)
        
        # Build field list for this row with commas
        field_parts = []
        for col in columns:
            if col in row and row[col] is not None:
                value = row[col]
                display_name_col = display_names.get(col, col)
                
                # Format special types
                if isinstance(value, str):
                    # Try to format as date first
                    formatted = _format_date_french(value)
                    if formatted != value:
                        value = formatted
                    elif len(value) > 100:
                        value = value[:100] + "..."
                elif isinstance(value, (int, float)):
                    if isinstance(value, float):
                        value = f"{value:.2f}"
                    else:
                        value = str(value)
                elif isinstance(value, (datetime, date)):
                    value = _format_date_french(value)
                
                field_parts.append(f"{display_name_col} {value}")
        
        # Join fields with commas and add period at the end
        if field_parts:
            parts.append(", ".join(field_parts) + ".")
    
    # Add "et il existe encore d'autres éléments" if there are more than 5
    if has_more:
        parts.append("et il existe encore d'autres éléments.")
    
    # Join everything with spaces
    return " ".join(parts)



