import asyncio
import json
import time
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

STATUS_FILE = 'status_g5.json'

console = Console()

async def monitor_status():
    """Monitora o status do g5.py e exibe informações em tempo real"""
    last_success = 0
    last_fail = 0
    
    # Inicializa o arquivo de status se não existir
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'running': False,
                'success': 0,
                'fail': 0,
                'errors': [],
                'last_update': time.time()
            }, f)
        console.print("[yellow]Arquivo de status inicializado.[/yellow]")
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Monitorando g5.py", total=100)
        
        while True:
            try:
                with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                
                if not status.get('running', False):
                    console.print(Panel.fit("[red]g5.py não está mais rodando ou foi sinalizado para parar."))
                    break
                
                success = status.get('success', 0)
                fail = status.get('fail', 0)
                last_update = status.get('last_update', 0)
                errors = status.get('errors', [])
                
                # Calcula progresso (apenas para visualização)
                total = success + fail
                if total > 0:
                    progress.update(task, completed=(success/total)*100)
                
                # Exibe informações formatadas
                console.print(Panel.fit(
                    Text.from_markup(f"""
                    [bold]Status do g5.py[/bold]
                    - Última atualização: {time.ctime(last_update)}
                    - Sucessos: [green]{success}[/green]
                    - Falhas: [red]{fail}[/red]
                    - Últimos erros: {errors[-3:] if errors else 'Nenhum erro'}
                    """),
                    title="[cyan]Monitoramento G5[/cyan]"
                ))
                
            except Exception as e:
                console.print(f"[red]Erro ao ler arquivo de status: {e}[/red]")

            await asyncio.sleep(10)  # verifica a cada 10 segundos

async def main():
    await monitor_status()

if __name__ == "__main__":
    asyncio.run(main())