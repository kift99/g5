# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import sys
import signal
import time
import threading
import json
from datetime import datetime

# Bibliotecas de terceiros
try:
    import aiosmtplib
    import aiofiles
    import dns.asyncresolver
    import dns.resolver
    from dotenv import load_dotenv
    from email_validator import validate_email, EmailNotValidError
    from email.message import EmailMessage
    from rich.logging import RichHandler
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError as e:
    print(f"❌ Biblioteca(s) faltando: {e.name}. Instale com: pip install aiosmtplib aiofiles dnspython python-dotenv email-validator rich")
    sys.exit(1)

# Carregar variáveis de ambiente
load_dotenv()

# Arquivo de status
STATUS_FILE = 'status_g5.json'

# Variável global de status
status_g5 = {
    'running': True,
    'success': 0,
    'fail': 0,
    'errors': [],
    'last_update': None
}

# Funções para manipular o arquivo de status
def save_status():
    global status_g5
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status_g5, f)
    except Exception as e:
        print(f"Erro ao salvar status: {e}")

def iniciar_status():
    global status_g5
    status_g5['running'] = True
    status_g5['success'] = 0
    status_g5['fail'] = 0
    status_g5['errors'] = []
    status_g5['last_update'] = time.time()
    save_status()

def parar_status():
    global status_g5
    status_g5['running'] = False
    status_g5['last_update'] = time.time()
    save_status()

def registrar_sucesso():
    global status_g5
    status_g5['success'] += 1
    status_g5['last_update'] = time.time()
    save_status()

def registrar_falha(msg=None):
    global status_g5
    status_g5['fail'] += 1
    if msg:
        status_g5['errors'].append(msg)
    status_g5['last_update'] = time.time()
    save_status()

# Thread que atualiza o arquivo de status periodicamente
def update_status_periodically():
    global status_g5
    while status_g5['running']:
        status_g5['last_update'] = time.time()
        save_status()
        time.sleep(60)  # atualiza a cada 60 segundos

# Iniciar thread de atualização de status
status_thread = threading.Thread(target=update_status_periodically, daemon=True)
status_thread.start()

# --- Aqui começa sua lógica principal ---

# Configurar console rich
console = Console()

# Função para mostrar o status atual
async def mostrar_status():
    """Mostra o status atual em um painel"""
    global status_g5
    
    # Calcula progresso
    total = status_g5.get('success', 0) + status_g5.get('fail', 0)
    progress = (status_g5.get('success', 0) / total * 100) if total > 0 else 0
    
    # Cria o painel de status
    status_text = Text.from_markup(f"""
    [bold]Status do Processamento[/bold]
    - Sucessos: [green]{status_g5.get('success', 0)}[/green]
    - Falhas: [red]{status_g5.get('fail', 0)}[/red]
    - Última atualização: {time.ctime(status_g5.get('last_update', 0))}
    - Progresso: [cyan]{progress:.1f}%[/cyan]
    """)
    
    console.clear()
    console.print(Panel.fit(status_text, title="[cyan]G5[/cyan]"))

async def monitorar_status():
    """Monitora e atualiza o status em tempo real"""
    while status_g5['running']:
        await mostrar_status()
        await asyncio.sleep(1)  # Atualiza a cada segundo

async def ler_emails():
    """Lê os emails do arquivo lista.txt"""
    try:
        async with aiofiles.open('lista.txt', 'r', encoding='utf-8') as f:
            emails = await f.readlines()
            return [email.strip() for email in emails if email.strip() and not email.strip().startswith('#')]
    except Exception as e:
        registrar_falha(f"Erro ao ler arquivo de emails: {str(e)}")
        return []

async def validar_email(email):
    """Valida um email usando email-validator"""
    try:
        v = validate_email(email)
        return True
    except EmailNotValidError as e:
        registrar_falha(f"Email inválido: {email} - {str(e)}")
        return False

async def processar_email(email):
    """Processa um email individual"""
    print(f"Processando email: {email}")
    await asyncio.sleep(1)  # Simula processamento
    return True  # Retorne False se houver falha

async def main():
    # Marca que o processamento começou
    iniciar_status()
    print("Início do processamento...")
    
    # Iniciar monitoramento de status
    monitor_task = asyncio.create_task(monitorar_status())
    
    try:
        # Ler emails do arquivo
        emails = await ler_emails()
        if not emails:
            print("Nenhum email válido encontrado!")
            return

        # Validar e processar cada email
        for email in emails:
            print(f"\nValidando email: {email}")
            if await validar_email(email):
                if await processar_email(email):
                    registrar_sucesso()
                else:
                    registrar_falha(f"Falha ao processar email: {email}")
            else:
                registrar_falha(f"Email inválido: {email}")

        print("Processamento concluído.")
    except Exception as e:
        # Caso ocorra erro inesperado
        registrar_falha(f"Erro inesperado: {str(e)}")
        print(f"Erro durante o processamento: {e}")

# Função para shutdown limpo ao receber sinais
async def graceful_shutdown(signal_number):
    print(f"\n[Sinal {signal_number}] Encerrando o processo limpo...")
    parar_status()

# Configurar sinais de interrupção
def setup_signals():
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda s, f: asyncio.create_task(graceful_shutdown(s)))

if __name__ == "__main__":
    # Configurar sinais
    setup_signals()

    # Marca início do processamento
    iniciar_status()

    try:
        # Executa o main assíncrono
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupção pelo teclado.")
    finally:
        # Marca que o processamento terminou
        parar_status()
        print("Encerrado.")