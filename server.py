import random
import math
from http.server import HTTPServer, BaseHTTPRequestHandler
import customtkinter
import threading
import json
import time
import base64


def logging():
    maintenant = time.localtime()
    annee = str(maintenant.tm_year)
    mois = str(maintenant.tm_mon).zfill(2)
    jour = str(maintenant.tm_mday).zfill(2)
    heure = str(maintenant.tm_hour).zfill(2)
    minute = str(maintenant.tm_min).zfill(2)
    seconde = str(maintenant.tm_sec).zfill(2)
    log = f"{annee}-{mois}-{jour} {heure}-{minute}-{seconde} | "
    return log


class Serveur(BaseHTTPRequestHandler):
    cle_privee = None
    modulo_n = None

    def Chiffrement(self):
        def VerificationNombrePremier(number):
            if number < 2:
                return False
            for i in range(2, number // 2 + 1):
                if number % i == 0:
                    return False
            return True

        def GenerationNombrePremier(min, max):
            premier = random.randint(min, max)
            while not VerificationNombrePremier(premier):
                premier = random.randint(min, max)
            return premier

        def Modulo(e, phi):
            for d in range(3, phi):
                if (d * e) % phi == 1:
                    return d
            raise ValueError("Le modulo n'a pas été trouvé")

        p, q = GenerationNombrePremier(1000, 5000), GenerationNombrePremier(1000, 5000)

        while p == q:
            q = GenerationNombrePremier(1000, 5000)

        n = p * q

        phi_n = (p - 1) * (q - 1)
        e = random.randint(3, phi_n - 1)
        while math.gcd(e, phi_n) != 1:
            e = random.randint(3, phi_n - 1)
        print("Clé publique (e) : ", e)
        print("Modulo (n) : ", n)
        d = Modulo(e, phi_n)
        print("Clé privée (d) : ", d)

        Serveur.cle_privee = d
        Serveur.modulo_n = n

        return e, n

    def do_POST(self):
        if not self.authenticate():
            self.send_response(401)
            self.send_header(
                "WWW-Authenticate", 'Basic realm="Authentication required"'
            )
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Authentication failed")
            return
        content_length = int(self.headers["Content-Length"])
        data = self.rfile.read(content_length)
        print("Received data: ", data)
        LOGS.insert(customtkinter.END, f"{logging()}Message chiffré reçu\n")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Donnee recue !")

        json_data = json.loads(data)
        ciphertext = json_data["ciphertext"]
        LOGS.insert(customtkinter.END, f"{logging()}Message chiffré : {ciphertext}\n")

        if Serveur.cle_privee is None or Serveur.modulo_n is None:
            LOGS.insert(
                customtkinter.END, f"{logging()}ERREUR: Clé privée non disponible!\n"
            )
            return

        message_dechiffre = [
            pow(ch, Serveur.cle_privee, Serveur.modulo_n) for ch in ciphertext
        ]
        message = "".join(chr(ch) for ch in message_dechiffre)
        LOGS.insert(customtkinter.END, f"{logging()}Message déchiffré : {message}\n")

    def do_GET(self):
        LOGS.insert(
            customtkinter.END, f"{logging()}Demande de clé publique entrante..\n"
        )
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        message = self.Chiffrement()
        self.wfile.write(str(message).encode())
        LOGS.insert(
            customtkinter.END, f"{logging()}Clé publique envoyée avec succès!\n"
        )

    def authenticate(self):
        auth_header = self.headers.get("Authorization")
        if auth_header:
            auth_decoded = base64.b64decode(auth_header.split(" ")[-1]).decode("utf-8")
            username, password = auth_decoded.split(":")
            if username == "admin" and password == "admin":
                return True
        return False


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
app = customtkinter.CTk()
app.title("Serveur HTTP | Chiffrement asymétrique ")
app.geometry("1000x550")


def lancement():
    print(ip.get())
    server_address = (ip.get(), int(port.get()))
    httpd = HTTPServer(server_address, Serveur)
    LOGS.insert(
        customtkinter.END,
        f"{logging()} Le serveur est en marche sur le port {port.get()} ...\n",
    )
    threading.Thread(target=httpd.serve_forever).start()


LOGS = customtkinter.CTkTextbox(app, width=730, height=400)
LOGS.place(x=200, y=70)
LOGS.insert(customtkinter.END, "")

button = customtkinter.CTkButton(master=app, text="Démarrer serveur", command=lancement)
button.place(x=10, y=80)

ip = customtkinter.CTkEntry(master=app, placeholder_text="IP serveur")
ip.place(x=10, y=15)
ip.insert(0, "127.0.0.1")

port = customtkinter.CTkEntry(master=app, placeholder_text="Port serveur")
port.place(x=10, y=45)
port.insert(0, "80")

app.mainloop()
