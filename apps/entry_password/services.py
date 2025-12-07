import requests, json
from coverage.debug import info_header
from .models import EntryPassword
from rest_framework.response import Response
from django.db import connection
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def get_new_entry_password():
    response = requests.get("http://docker_go:8080/entry_password", timeout=2)
    payload = response.json()
    logging.info("new payload: %s", payload)
    return payload


def save_new_entry_password():
    logging.info("Detected new changes for entry password")
    payload = get_new_entry_password()
    logging.info("New entry password received: %s", payload)
    old_password = EntryPassword.objects.filter().first()
    query = """
        UPDATE entry_password
        SET 
            entry_password = %s, 
            last_updated = %s
        WHERE id = %s;
    """
    params = [payload.get("entry_password"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),old_password.id]
    
    with connection.cursor() as cursor:
        cursor.execute(query,params)

    logging.info("entry password updated: %s", type(datetime.now().strftime("%Y-%m-%d %H:%M")))

