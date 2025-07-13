import base64
import lib_alloggiatiweb
import xml.etree.ElementTree as ET
import os

def test_file(filename):
    # Implementa la logica per testare il file
    # Ad esempio, potresti voler verificare se il file esiste
    try:
        with open(filename, 'r') as file:
            content = file.read()
            # Aggiungi qui altre verifiche sul contenuto del file
            print(f"File '{filename}' read successfully.")
            righe = lib_alloggiatiweb.leggi_righe_da_file(filename)
            if righe.__len__() == 0:
                print("File " + filename + " is empty or not found.")
                return
            lib_alloggiatiweb.send_alloggiatiwebTest(righe)
            return True
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        return False
    
def invia_file(filename):
    # Implementa la logica per inviare il file
    try:
        with open(filename, 'rb') as file:
            content = file.read()
            # Aggiungi qui la logica per inviare il file
            print(f"File '{filename}' inviato con successo.")
            righe = lib_alloggiatiweb.leggi_righe_da_file(filename)
            if righe.__len__() == 0:
                print("File " + filename + " is empty or not found.")
                return
            lib_alloggiatiweb.send_alloggiatiwebSend(righe)
            return True
    except Exception as e:
        print(f"Error sending file '{filename}': {e}")
        return False
    
def anonimizza_dati(path, filename):
    # Implementa la logica per anonimizzare i dati sensibili nel file
    try:
        print(f"0Anonimizing path '{path}' - file '{filename}'")
        with open(os.path.join(path, filename), 'r') as file:
            print(f"Anonimizing file '{file}'...")
            content = file.read()
            # Aggiungi qui la logica per anonimizzare i dati
            # Esempio di anonimizzazione: sostituzione di tutte le lettere con 'X'
            content = ''.join(['X' if c.isalpha() else c for c in content])
            with open(os.path.join(path, f'{filename}'), 'w') as anonymized_file:
                anonymized_file.write(content)
            print(f"File '{filename}' anonymized successfully.")
            return content
    except Exception as e:
        print(f"Error anonymizing file '{filename}': {e}")
        return None

def scarica_ricevuta(path, filename, ricevuta_path):
    # Implementa la logica per scaricare la ricevuta
    try:
        with open(os.path.join(path, filename), 'rb') as file:
            content = file.read()
            date = filename.replace('.txt', '')
            date = date.replace('quest-', '')
            res = lib_alloggiatiweb.ricevuta(date)
            if not res:
                print(f"Ricevuta '{date}' non trovata.")
                return
            print(f"Ricevuta '{date}' scaricata con successo.")
            #cerco il campo PDF (array di byte base64) e lo salvo in un file
            if res:
                root = ET.fromstring(res)
                ns = {
                    'soap': 'http://www.w3.org/2003/05/soap-envelope',
                    'all': 'AlloggiatiService'
                }
                pdf_data = root.find('.//all:PDF', ns)
                if pdf_data is not None:
                    with open(f'ricevute/ricevuta_{date}.pdf', 'wb') as f:
                        #pdf_data.text è un base64, lo decodifico e lo salvo
                        print(f"Downloading ricevuta '{filename}' to '{ricevuta_path}'.")
                        f.write(base64.b64decode(pdf_data.text))
    except Exception as e:
        print(f"Error downloading ricevuta '{filename}': {e}")
        return None
    print(f"Ricevuta '{filename}' saved to '{ricevuta_path}'.")
    # anonimizza i dati sensibili nel file
    content = anonimizza_dati(path, filename)
    return content