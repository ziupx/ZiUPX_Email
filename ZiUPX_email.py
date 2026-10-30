import os
import sys
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
import hashlib # Для Gravatar

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
[bold green]   [+] ZiUPX Email Detective v1.1[/bold green]
[bold white]   [+] Multi-Source OSINT Tool[/bold white]
    """
    console.print(Align.center(banner))
    console.print("[bold yellow]═══════════════════════════════════════════════════════════[/bold yellow]\n")

def check_leaks(email):
    """Проверяет email через несколько источников"""
    console.print(f"\n[yellow][*] Глубокий поиск утечек для {email}...[/yellow]")
    all_leaks = []

    # 1. Источник 1: XposedOrNot
    try:
        url = f"https://api.xposedornot.com/v1/check-email/{email}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'breaches' in data and data['breaches']:
                all_leaks.extend(data['breaches'])
    except:
        pass

    # 2. Источник 2: LeakCheck (публичный API)
    try:
        # LeakCheck имеет открытый API для проверки (без ключа, но с лимитами)
        url = f"https://leakcheck.io/api/public?key=&check={email}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('found'):
                # Добавляем названия баз, если они есть
                for source in data.get('sources', []):
                    all_leaks.append(source.get('name', 'Неизвестная база (LeakCheck)'))
    except:
        pass

    # Убираем дубликаты
    return list(set(all_leaks))

def check_platforms(email):
    console.print(f"\n[yellow][*] Проверка регистраций на платформах...[/yellow]")
    results = {}
    
    # GitHub
    try:
        url = f"https://api.github.com/search/users?q={email}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200 and response.json().get('total_count', 0) > 0:
            results['GitHub'] = "Аккаунт найден"
    except:
        pass
        
    # Gravatar
    try:
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            results['Gravatar'] = "Есть аватарка (email активен)"
    except:
        pass

    return results

# ... (функция main остается без изменений, но можно добавить вывод, если ничего не найдено)