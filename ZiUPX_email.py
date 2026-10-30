import os
import sys
import requests
import hashlib
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

console = Console()

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = """
[bold cyan]
███████╗██╗██╗   ██╗██████╗ ██╗  ██╗
╚══███╔╝██║██║   ██║██╔══██╗╚██╗██╔╝
  ███╔╝ ██║██║   ██║██████╔╝ ╚███╔╝ 
 ███╔╝  ██║██║   ██║██╔═══╝  ██╔██╗ 
███████╗██║╚██████╔╝██║     ██╔╝ ██╗
╚══════╝╚═╝ ╚═════╝ ╚═╝     ╚═╝  ╚═╝
[/bold cyan]
[bold green]   [+] ZiUPX Email Detective v1.2[/bold green]
[bold white]   [+] Direct OSINT Checker[/bold white]
    """
    console.print(Align.center(banner))
    console.print("[bold yellow]═══════════════════════════════════════════════════════════[/bold yellow]\n")

def check_email_direct(email):
    console.print(f"\n[cyan][*] Прямая проверка для {email}...[/cyan]")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    results = {}

    # 1. Проверка Gravatar (активность email)
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    try:
        r = requests.get(f"https://www.gravatar.com/avatar/{email_hash}?d=404", timeout=5, headers=headers)
        if r.status_code == 200:
            results["Gravatar"] = "[green]Активен (есть аватар)[/green]"
        else:
            results["Gravatar"] = "[red]Не найден[/red]"
    except Exception:
        results["Gravatar"] = "[yellow]Ошибка проверки[/yellow]"

    # 2. Проверка GitHub (через публичный поиск)
    try:
        r = requests.get(f"https://api.github.com/search/users?q={email}", timeout=5, headers=headers)
        if r.status_code == 200:
            data = r.json()
            if data.get('total_count', 0) > 0:
                results["GitHub"] = f"[green]Найден ({data['total_count']} совпадений)[/green]"
            else:
                results["GitHub"] = "[red]Не найден[/red]"
    except Exception:
        results["GitHub"] = "[yellow]Ошибка API[/yellow]"

    # Вывод результатов
    console.print("\n")
    if results:
        table = Table(title="[bold green]Результаты прямой проверки[/bold green]", border_style="cyan")
        table.add_column("Сервис", style="cyan")
        table.add_column("Статус", style="white")
        
        for service, status in results.items():
            table.add_row(service, status)
            
        console.print(table)
    else:
        console.print("[bold red][!] Не удалось получить данные.[/bold red]")

if __name__ == "__main__":
    print_banner()
    console.print("[bold cyan]Введите email для прямой проверки (например, test@example.com):[/bold cyan]")
    email = input("> ").strip()
    check_email_direct(email)