#library for sending info to alloggiatiweb
import xml
import requests
import json
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()
import os
# Load environment variables
url = os.getenv("URL")
dataUser = {
    'username': os.getenv("USERNAME"),
    'password': os.getenv("PASSWORD"),
    'wskey': os.getenv("WSKEY"),
    'token': ''
}
def ricevuta(date):
    """
    Download the receipt for the given date.
    
    :param date: Date for which to download the receipt.
    :return: Content of the receipt file.
    """
    if( not dataUser['token']):
        res = generateToken()
        if not res:
            print("Failed to generate token.")
            return None
    body = f'<all:Data>{date}T00:00:00</all:Data>'
    print("Body Ricevuta:", body)
    response = send(url, 'Ricevuta', body, 'RicevutaResponse/RicevutaResult')
    print("Response Ricevuta:", response)
    return response

def send_alloggiatiwebSend(righe):
    send_alloggiatiweb('Send', righe)

def send_alloggiatiwebTest(righe):
    send_alloggiatiweb('Test', righe)
def send_alloggiatiweb(ope, righe):
    """
    Send data to AlloggiatiWeb API.
    
    :param data: Dictionary containing the data to be sent.
    :param url: URL of the AlloggiatiWeb API endpoint.
    :return: Response from the API.
    """
    if( not dataUser['token']):
        res = generateToken()
        if not res:
            print("Failed to generate token.")
            return None
    elencoSched1 = ''
    for riga in righe:
        if riga.strip() == '':
            continue
        elencoSched1 += '<all:string>' + riga + '</all:string>'
    elencoSched = '<all:ElencoSchedine>' + elencoSched1 + '</all:ElencoSchedine>'
    try:
        ##response = send(url, ope, elencoSched, 'TestResponse/TestResult')
        response = send(url, ope, elencoSched, 'SendResponse/SendResult>')
        # gestisci la risposta XML
        if response:
            root = ET.fromstring(response)
            ns = {
                'soap': 'http://www.w3.org/2003/05/soap-envelope',
                'all': 'AlloggiatiService'
            }
            result = root.find('.//all:SchedineValide', ns)
            if result is not None and str(result.text) != str(righe.__len__()):
                print("Schedine validate:", result.text + " di " + str(righe.__len__()))
                return result.text, response
            else:
                print("Schedine validate:", result.text + " di " + str(righe.__len__()))
                print("E' possibile procedere con l'invio.")
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to AlloggiatiWeb: {e}")
        return None
    
def leggi_righe_da_file(filename):
    """
    Legge tutte le righe da un file di testo e restituisce una lista di stringhe.
    :param filename: Percorso del file da leggere.
    :return: Lista di stringhe, una per ogni riga del file.
    """
    righe = []
    try:
        with open('schedine/'+filename, 'r', encoding='utf-8') as f:
            righe = [line.rstrip('\n') for line in f]
    except Exception as e:
        print(f"Errore nella lettura del file {filename}: {e}")
    return righe

def generateToken():
    """
    Authenticate with AlloggiatiWeb API.
    
    :param username: Username for authentication.
    :param password: Password for authentication.
    :return: Authentication token or None if authentication fails.
    """
    response = send(url, 'GenerateToken', '', 'all:GenerateTokenResult/all:token')
    if response:
        # gestisci la risposta XML
        root = ET.fromstring(response)
        ns = {
            'soap': 'http://www.w3.org/2003/05/soap-envelope',
            'all': 'AlloggiatiService'
        }
        token = root.find('.//all:token', ns)
        if token is not None:
            dataUser['token'] = token.text
            print("Token generated:", dataUser['token'])
            return dataUser['token'], response
        return response
    return None

def send(url, ope, body, returnData):
    """ Send authentication request to AlloggiatiWeb API.
    :param url: URL of the AlloggiatiWeb API endpoint.
    :param auth: Authentication data (username, password, wskey).
    :param ope: Operation type (e.g., 'GenerateToken').
    :return: Response from the API.
    """
    headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
    payload = '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:all="AlloggiatiService">'
    payload += '<soap:Header/><soap:Body><all:' + ope + '>'
    payload += '<all:Utente>' + dataUser['username'] + '</all:Utente>'
    if ope == 'GenerateToken':
        payload += '<all:Password>' + dataUser['password'] + '</all:Password>'
        payload += '<all:WsKey>' + dataUser['wskey'] + '</all:WsKey>'
    else:
        payload += '<all:token>' + dataUser['token'] + '</all:token>'
    payload += body
    payload += '</all:' + ope + '></soap:Body></soap:Envelope>'
    print("Payload:", payload)
    print("Url:", url+'?op='+ope)
    resWs = requests.post(url+'?op='+ope, headers=headers, data=payload)
    
    if resWs.status_code == 200:
        return resWs.text
    else:
        print(f"Error: {resWs.status_code} - {resWs.text}")
        return ''
    

# ...existing code...

def main():
    oper = True
    filename = 'quest-2025-07-11.txt'
    righe = leggi_righe_da_file(filename)
    if righe.__len__() == 0:
        print("File " + filename + " is empty or not found.")
        return
    # Qui puoi mettere il codice che vuoi eseguire all'avvio
    res = generateToken()
    if not res:
        print("Failed to generate token.")
        return
    print("Token generated successfully.")
    # Example of sending data
    res = send_alloggiatiwebSend(righe)
    if res:
        print("Procedo all'invio delle schedine.")
    else:
        print("Errori nelle schedine. xml:"+res[1])

if __name__ == "__main__":
    main()