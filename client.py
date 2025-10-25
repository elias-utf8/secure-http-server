import requests
import time


time.sleep(2)
url = "http://127.0.0.1:8080"
print("Connexion au serveur...")
response = requests.get(url)
paquet = response.content.decode("utf-8").strip("b'")

valeur_sans_parentheses = paquet[1:-1]
e, n = valeur_sans_parentheses.split(", ")
e = int(e)
n = int(n)
print(f"Clé publique reçue: e={e}, n={n}")
print("Vous pouvez maintenant envoyer des messages chiffrés.\n")

while True:
    message = input("> ")
    message_encoded = [ord(ch) for ch in message]

    ciphertext = [pow(ch, e, n) for ch in message_encoded]
    print(
        f"Message chiffré: {ciphertext[:5]}..."
        if len(ciphertext) > 5
        else f"Message chiffré: {ciphertext}"
    )

    data = {"ciphertext": ciphertext}
    response = requests.post(url, json=data, auth=("admin", "admin"))
    print(f"Réponse du serveur: {response.status_code} - {response.text}\n")
