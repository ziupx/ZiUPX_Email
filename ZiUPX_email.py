import os
import sys
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
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
[bold green]   [+] ZiUPX Email Detective v1.0[/bold green]
[bold white]   [+] OSINT Tool for Email Investigation[/bold white]
    """
    console.print(Align.center(banner))
    console.print("[bold yellow]═══════════════════════════════════════════════════════════[/bold yellow]\n")

def check_leaks(email):
    """Проверяет email в базе утечек XposedOrNot"""
    console.print(f"\n[yellow][*] Проверка утечек для {email}...[/yellow]")
    try:
        # XposedOrNot - бесплатный API для проверки утечек
        url = f"https://api.xposedornot.com/v1/check-email/{email}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # API возвращает данные в виде списка или словаря
            if 'breaches' in data and data['breaches']:
                return data['breaches']
            elif 'email' in data and 'breaches' in data:
                return data['breaches']
    except Exception:
        pass
    return []

def check_platforms(email):
    """Проверяет регистрацию на популярных платформах"""
    console.print(f"\n[yellow][*] Проверка регистраций на платформах...[/yellow]")
    
    # Мы не будем ломиться на сайты, а используем открытые API-проверки
    results = {}
    
    # GitHub (используем поиск пользователей по email)
    try:
        url = f"https://api.github.com/search/users?q={email}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200 and response.json().get('total_count', 0) > 0:
            results['GitHub'] = "Аккаунт найден"
    except:
        pass
        
    # Have I Been Pwned (через прокси API)
    # (В реальности HIBP требует ключ, поэтому мы просто покажем заглушку)
    
    # Можно добавить проверку Gravatar (если есть аватарка, значит email используется)
    try:
        import hashlib
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            results['Gravatar'] = "Есть аватарка (email активен)"
    except:
        pass

    return results

def main():
    print_banner()
    console.print("[bold cyan]Введите email для расследования (например, test@example.com):[/bold cyan]")
    target_email = input("> ").strip()
    
    if not target_email or '@' not in target_email:
        console.print("[red][!] Некорректный email.[/red]")
        return

    # 1. Проверка утечек
    leaks = check_leaks(target_email)
    
    if leaks:
        table = Table(title="[bold red]Найдено в утечках![/bold red]", border_style="red")
        table.add_column("Название утечки", style="white")
        table.add_column("Дата", style="yellow")
        
        for leak in leaks:
            if isinstance(leak, dict):
                name = leak.get('name', 'Неизвестно')
                date = leak.get('date', 'Неизвестно')
                table.add_row(name, date)
            else:
                table.add_row(str(leak), "Информация скрыта")
                
        console.print(table)
    else:
        console.print("[bold green][✓] Этот email не найден в известных публичных утечках.[/bold green]")

    # 2. Проверка платформ
    platforms = check_platforms(target_email)
    
    if platforms:
        table = Table(title="[bold cyan]Найденные регистрации[/boldcyan]", border_style="cyan")
        table.add_column("Платформа", style="cyan")
        table.add_column("Статус", style="green")
        
        for platform, status in platforms.items():
            table.add_row(platform, status)
            
        console.print(table)
    else:
        console.print("[bold yellow][*] Активных регистраций на популярных платформах не найдено (или они скрыты).[/bold yellow]")

    console.print("\n[bold blue]Расследование завершено.[/bold blue]")

if __name__ == "__main__":
    main()
