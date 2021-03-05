import base64
import json
import re

import requests
from bs4 import BeautifulSoup


def decode_base64(data: str):
    data = re.sub(rb'[^a-zA-Z0-9+/]', b'', data.encode())[:162]
    return base64.b64decode(data + b'=' * (-len(data) % 4)).decode("cp437")[1:]


def sid_to_uid(SID: str):
    try:
        decoded_uid = decode_base64(SID)
        uid = decoded_uid.split('"2": ')[1][:38].replace("\"", "")
        return uid
    except json.decoder.JSONDecodeError:
        return sid_to_uid_2(SID)


def sid_to_ip_address(SID: str):
    try:
        return json.loads(decode_base64(SID))["4"]
    except json.decoder.JSONDecodeError:
        return sid_to_ip_address_2(SID)


def sid_to_uid_2(SID: str):
    data = f'input={SID}&charset=UTF-8'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post('https://www.base64decode.org/', data, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    output = soup.find('textarea', {'id': 'output'})
    uid = output.text.split(':')[4].split(',')[0].replace('"', '').replace(' ', '')

    return uid


def sid_to_ip_address_2(SID: str):
    data = f'input={SID}&charset=UTF-8'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post('https://www.base64decode.org/', data, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    output = soup.find('textarea', {'id': 'output'})
    ip_address = output.text.split(':')[6].split(',')[0].replace('"', '').replace(' ', '')

    return ip_address
