import requests
import asebot.config

def load_books():
    response = requests.get(asebot.config.ENDPOINT_BOOKS)
    return response.json()
