import os
import sys
import time
import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align

console = Console()

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = """
[bold white]
███████╗██╗██╗   ██╗██████╗ ██╗  ██╗
╚══███╔╝██║██║   ██║██╔══██╗╚██╗██╔╝
  ███╔╝ ██║██║   ██║██████╔╝ ╚███╔╝ 
 ███╔╝  ██║██║   ██║██╔═══╝  ██╔██╗ 
███████╗██║╚██████╔╝██║     ██╔╝ ██╗
╚══════╝╚═╝ ╚═════╝ ╚═╝     ╚═╝  ╚═╝
[/bold white]
[bold cyan]   ZiUPX Recon Framework v2.1[/bold cyan]
[bold white]   Professional OSINT Engine[/bold white]
    """
    console.print(Align.center(banner))
    console.print("[bold white]═══════════════════════════════════════════════════════════[/bold white]\n")

def check_gravatar(email):
    import hashlib
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    try:
        r = requests.get(f"https://www.gravatar.com/avatar/{email_hash}?d=404", timeout=5)
        return "Активен" if r.status_code == 200 else "Не найден"
    except:
        return "Ошибка"

def check_github(email):
    try:
        headers = {"User-Agent": "ZiUPX-Recon/2.1"}
        r = requests.get(f"https://api.github.com/search/users?q={email}", headers=headers, timeout=5)
        if r.status_code == 200 and r.json().get('total_count', 0) > 0:
            return f"Найден ({r.json()['total_count']})"
        return "Не найден"
    except:
        return "Ошибка"

def check_telegram(username):
    """Проверяет, существует ли пользователь в Telegram по никнейму"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://t.me/{username}"
        r = requests.get(url, headers=headers, timeout=5)
        
        # Если страница содержит "tgme_page_title", значит профиль существует
        if r.status_code == 200 and "tgme_page_title" in r.text:
            return "Активен"
        return "Не найден"
    except:
        return "Ошибка"

def check_tiktok(username):
    """Проверяет, существует ли пользователь в TikTok"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        url = f"https://www.tiktok.com/@{username}"
        r = requests.get(url, headers=headers, timeout=5)
        
        # Если страница загружается и не содержит "Couldn't find this account"
        if r.status_code == 200 and "Couldn't find this account" not in r.text:
            return "Активен"
        return "Не найден"
    except:
        return "Ошибка"

def main():
    print_banner()
    
    console.print("[bold white]Выберите тип разведки:[/bold white]")
    console.print("[cyan]1.[/cyan] Поиск по Email")
    console.print("[cyan]2.[/cyan] Поиск по Никнейму (Telegram, TikTok, GitHub)")
    console.print("[cyan]0.[/cyan] Выход")
    
    choice = input("\n> ").strip()
    
    if choice == "1":
        target = input("[bold cyan]Введите Email: [/bold cyan]").strip()
        if not target or '@' not in target:
            console.print("[bold red]Ошибка: Некорректный Email.[/bold red]")
            return
            
        console.print(f"\n[bold yellow][*] Запуск модулей для {target}...[/bold yellow]\n")
        
        results = {}
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="[cyan]Gravatar...", total=None)
            results["Gravatar"] = check_gravatar(target)
            progress.add_task(description="[cyan]GitHub (Email)...", total=None)
            results["GitHub"] = check_github(target)

        table = Table(title="[bold white]Отчет OSINT: Email[/bold white]", border_style="white", show_header=True, header_style="bold cyan")
        table.add_column("Сервис", style="white")
        table.add_column("Статус", style="white")
        
        for service, status in results.items():
            color = "green" if status in ["Активен", "Найден"] or "Найден" in status else "red"
            table.add_row(service, f"[{color}]{status}[/{color}]")
            
        console.print(table)

    elif choice == "2":
        target = input("[bold cyan]Введите Никнейм (без @): [/bold cyan]").strip()
        if not target:
            return
            
        console.print(f"\n[bold yellow][*] Запуск модулей для {target}...[/bold yellow]\n")
        
        results = {}
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="[cyan]Telegram...", total=None)
            results["Telegram"] = check_telegram(target)
            
            progress.add_task(description="[cyan]TikTok...", total=None)
            results["TikTok"] = check_tiktok(target)
            
            progress.add_task(description="[cyan]GitHub...", total=None)
            # Для GitHub используем поиск по нику (через юзернейм)
            try:
                headers = {"User-Agent": "ZiUPX-Recon/2.1"}
                r = requests.get(f"https://api.github.com/users/{target}", headers=headers, timeout=5)
                results["GitHub"] = "Активен" if r.status_code == 200 else "Не найден"
            except:
                results["GitHub"] = "Ошибка"

        table = Table(title="[bold white]Отчет OSINT: Username[/bold white]", border_style="white", show_header=True, header_style="bold cyan")
        table.add_column("Платформа", style="white")
        table.add_column("Статус", style="white")
        
        for service, status in results.items():
            color = "green" if status == "Активен" else "red"
            table.add_row(service, f"[{color}]{status}[/{color}]")
            
        console.print(table)

if __name__ == "__main__":
    main()