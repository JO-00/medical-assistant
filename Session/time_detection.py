import json
from datetime import datetime, timedelta
from LLM_API import call_ollama
import regex as re

def calculate_appointment_live(llm_json, language="fr"):
    final_date = datetime.now()
    
    abs_date = llm_json.get("absolute_date", {}) or {}
    wk_target = llm_json.get("weekday_target", {}) or {}
    jump = llm_json.get("relative_jump", {}) or {}
    t_block = llm_json.get("time", {}) or {}
    
    # 1. Handle Absolute Dates (e.g., "le seize juillet", "December 25th")
    if abs_date.get("day") is not None and abs_date.get("month"):
        months_en = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        months_fr = {
            'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
            'juillet': 7, 'août': 8, 'aout' :8 , 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12 , 'decembre' : 12
        }
        months_map = {**months_en, **months_fr}
        
        month_num = months_map.get(str(abs_date["month"]).lower())
        if month_num:
            try:
                final_date = final_date.replace(month=month_num, day=int(abs_date["day"]))
            except ValueError:
                # Fallback safeguard for invalid dates like Feb 30th
                pass

    # 2. Handle Relative Jumps (e.g., "dans 3 jours", "tomorrow")
    if jump and jump.get("unit"):
        unit = jump["unit"]
        amount = jump["amount"] if jump["amount"] is not None else 1
        
        unit_map = {
            "hour": timedelta(hours=amount),
            "day": timedelta(days=amount),
            "week": timedelta(weeks=amount),
            "month": timedelta(days=amount * 30),
            "year": timedelta(days=amount * 365)
        }
        final_date += unit_map.get(unit, timedelta(0))

    # 3. Handle Weekdays - Bilingual (e.g., "mardi prochain")
    if wk_target and wk_target.get("weekday"):
        weekdays_en = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        weekdays_fr = {
            'lundi': 0, 'mardi': 1, 'mercredi': 2, 'jeudi': 3,
            'vendredi': 4, 'samedi': 5, 'dimanche': 6
        }
        weekdays = {**weekdays_en, **weekdays_fr}
        
        target_day_num = weekdays.get(str(wk_target["weekday"]).lower())
        
        if target_day_num is not None:
            current_day_num = final_date.weekday()
            days_ahead = (target_day_num - current_day_num) % 7
            
            # If it's the same day of the week but flagged as 'next/prochain', jump 7 days ahead
            if days_ahead == 0 or wk_target.get("is_relative_next"):
                days_ahead += 7

            final_date += timedelta(days=days_ahead)

    # 4. Dynamic Time Extraction & Mask Formatting
    date_str = final_date.strftime("%Y-%m-%d")
    
    # If it was a generic hourly delta ("dans 3 heures"), extract the direct math result
    if jump and jump.get("unit") == "hour":
        return f"{date_str} {final_date.hour:02d}:{final_date.minute:02d}:00"
        
    # If the hour element is missing completely from parsing, fallback to unknown time mask
    if t_block.get("hour") is None:
        return f"{date_str} XX:XX"
        
    # Standard time resolution: missing minutes fallback deterministically to 00
    hour = int(t_block.get("hour"))
    minute = int(t_block.get("minute")) if t_block.get("minute") is not None else 0
    
    return f"{date_str} {hour:02d}:{minute:02d}:00"




with open("Router/Contexts/time_detection/fr.txt") as f:
    french_context = f.read()
with open("Router/Contexts/time_detection/en.txt") as f:
    english_context = f.read()



def contains_temporal_intent(prompt: str) -> bool:
    """Deterministically check if a prompt contains temporal intent (time/date references)."""
    #currently very fragile and weak, example, "next patient" is a false positive, will be enhanced in the future
    prompt_lower = prompt.lower()
    
    # English temporal keywords
    en_keywords = [
        "today", "tomorrow", "yesterday", "next", "last",
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "january", "february", "march", "april", "may", "june", "july", "august", 
        "september", "october", "november", "december"
        "hour", "hours", "minute", "minutes", "o'clock", "am", "pm", 
        "morning", "afternoon", "evening", "night",
        "date", "time", "week", "month", "year", "day",
        "in", "ago", "from now", "later", "earlier",
        "appointment", "schedule", "booking", "meet"
    ]
    
    # French temporal keywords
    fr_keywords = [
        "aujourd'hui", "demain", "hier", "prochain", "dernier",
        "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche",
        "janvier", "février","fevrier" , "mars", "avril", "mai", "juin", "juillet", "août" "aout",
        "septembre", "octobre", "novembre", "décembre" , "decembre",
        "heure", "heures", "minute", "minutes", "midi", "minuit",
        "matin", "après-midi" , "soir", "nuit",
        "date", "temps", "semaine", "mois", "année", "jour",
        "dans", "plus tard", "plus tôt",
        "rendez-vous", "planification", "réservation", "rencontrer"
    ]
    
    # Check for any temporal keywords
    for keyword in en_keywords + fr_keywords:
        if keyword in prompt_lower:
            return True
    
    # Check for time patterns like "2pm", "14:30", "3 heures", etc.
    # English time patterns
    import re
    time_patterns = [
        r'\d{1,2}:\d{2}',  # 14:30
        r'\d{1,2}\s?(?:am|pm)',  # 2pm, 2 pm
        r'\d{1,2}\s?h(?:eures?)?',  # 3h, 3 heures (French)
        r'\d{1,2}\s?o\'?clock',  # 2 o'clock
    ]
    
    for pattern in time_patterns:
        if re.search(pattern, prompt_lower):
            return True
    
    return False

import re
import json

def extract_time(input: str, language: str):
    assert language in ["en", "fr"]

    # 1. HARD GATEKEEPER: Check if temporal keywords exist first
    if not contains_temporal_intent(input):
        print("DEBUG: Zero temporal intent detected. Returning completely blank mask.")
        return "XXXX-XX-XX XX:XX", {
            "time_string_literal": None,
            "absolute_date": {"day": None, "month": None},
            "weekday_target": {"weekday": None, "is_relative_next": False},
            "relative_jump": {"unit": None, "amount": None},
            "time": {"hour": None, "minute": None}
        }

    try:
        system_prompt = english_context if language == "en" else french_context
        response = call_ollama(
            user_message=input,
            system_prompt=system_prompt
        )
        extracted_json = json.loads(response) if isinstance(response, str) else response
        
        # ANCHOR FIX: If it's still a string due to double serialization, strip the inner layer
        if isinstance(extracted_json, str):
            extracted_json = json.loads(extracted_json)
    except Exception as e:
        print(f"Error parsing LLM payload: {e}")
        return "XXXX-XX-XX XX:XX", {
            "time_string_literal": None,
            "absolute_date": {"day": None, "month": None},
            "weekday_target": {"weekday": None, "is_relative_next": False},
            "relative_jump": {"unit": None, "amount": None},
            "time": {"hour": None, "minute": None}
        }
    
    # Normalize nested blocks gracefully to handle missing or None structures safely
    print(type(extracted_json))
    abs_date = extracted_json.get("absolute_date") or {}
    wk_target = extracted_json.get("weekday_target") or {}
    jump = extracted_json.get("relative_jump") or {}
    t_block = extracted_json.get("time") or {}
    
    # 2. RIGOROUS GUARD: Check if the LLM parsed absolutely nothing structural
    # Includes the fix to let absolute dates (e.g., 'day': 16) bypass the fallback mask!
    if (not (isinstance(abs_date, dict) and abs_date.get("day")) and 
        not (isinstance(wk_target, dict) and wk_target.get("weekday")) and 
        not (isinstance(jump, dict) and jump.get("unit")) and 
        (not isinstance(t_block, dict) or t_block.get("hour") is None)):
        return "XXXX-XX-XX XX:XX", extracted_json

    # 3. Calculate absolute target timestamp
    extracted_time = calculate_appointment_live(extracted_json, language)
    
    # Validate the final output pattern against your strict ISO regex mask
    iso_datetime_regex = r"^(?:\d{4}|XX)-(?:\d{2}|XX)-(?:\d{2}|XX)\s(?:\d{2}|XX):(?:\d{2}|XX)(?::(?:\d{2}|XX))?$"
    assert re.match(iso_datetime_regex, extracted_time), f"Assertion Error: Format invalid '{extracted_time}'"
    
    return extracted_time, extracted_json


#EXTERNAL
def insert_time(prompt : str , language : str = "en") -> str:
    extracted_time , extracted_json = extract_time(prompt , language)
    if extracted_time == "XXXX-XX-XX XX:XX" : 
        return prompt
    substr = extracted_json["time_string_literal"]

    if not substr or substr not in prompt :
        return prompt + f" <indication> the time  implied is {extracted_time} </indication>"
    
    prompt  = prompt.replace(extracted_json['time_string_literal'] , extracted_time) 
    
    return prompt



#for debugging purposes only
if __name__ == "__main__" :
    from mock_ollama_call import call_ollama
    while 1:
        print(insert_time(input("INPUT = ") ,input("Enter your language = ")))
