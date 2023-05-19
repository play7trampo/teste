from flask import Flask, jsonify
from pynubank import Nubank, MockHttpClient
import os
import random
import string
import requests
from getpass import getpass
import json
from colorama import init, Fore, Style
from pynubank import NuException
from pynubank.utils.certificate_generator import CertificateGenerator




def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


def log(message, color=Fore.BLUE):
    print(f'{color}{Style.DIM}[*] {Style.NORMAL}{Fore.LIGHTBLUE_EX}{message}')


def save_cert(cert, name):
    path = os.path.join(os.getcwd(), name)
    with open(path, 'wb') as cert_file:
        cert_file.write(cert.export())






app = Flask(__name__)




@app.route("/")
def inicial():
    
    return {"Status": "API FUNCIONANDO"}


junto = {}

junto = []



@app.route("/certificado/<cpf>/<senha>")
def main(cpf, senha):
    init()
    device_id = generate_random_id()
    cpf = cpf
    password = senha

    generator = CertificateGenerator(cpf, password, device_id) ## AQUI GERA O CODIGO PRA ENVIAR 

    junto2 = {cpf : {"cpf": cpf, "chave": generator}}
    try:
        email = generator.request_code() # AQUI ELE ENVIA O CODIGO PARA O EMAIL
    except NuException:
        log(f'{Fore.RED}CPF OU SENHA INVALIDA', Fore.RED)
        return
    
    for i, item in enumerate(junto):
        if cpf in item:
            junto.pop(i)
            break

    junto.append(junto2)
    
    return {"email": email}



@app.route("/perfilcompleto/<cpf>/<senha>/<certificado>")
def obter_perfilcompleto(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)
    debito = nu.get_account_balance()
    perfil = nu.get_customer()
    info_card = nu.get_credit_card_balance()
    
    limite_disponivel = info_card.get('available', 'Limite disponivel não encontrado')
    
    fatura_atual = info_card.get('open', 'Fatura atual não encontrado')
    
    proximas_faturas = info_card.get('future', 'Fatura atual não encontrado')
    
    return {"Saldo": debito ,"dados": perfil,"limitedisponivel": limite_disponivel,
            "faturaatual": fatura_atual,
            "proximasfaturas": proximas_faturas
            }



@app.route("/codigo/<codigo>/<cpf>")
def enviarcodigo(codigo, cpf):

   
    code = codigo
    cpf = cpf

    for item in junto:
        if cpf in item:
            if "chave" in item[cpf]:
                chave = item[cpf]["chave"]
                cert1, cert2 = chave.exchange_certs(code)
                save_cert(cert1, (codigo+'.p12'))
                return {"mensagem": "Certificado Gerado com sucesso!"}
            else:
                log(f'Chave "chave" não encontrada para o CPF {cpf}')
        else:
                log(f'CPF {cpf} não encontrado')






if __name__ == "__main__":
    app.run(debug=True)
