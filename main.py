# /// script
# dependencies = [
#   "click",
#   "rich",
# ]
# ///

import os
import socket
import statistics
import sys
import time
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table

# Instância global para o terminal
console = Console()


def calculate_stats(latencies):
    if not latencies:
        return 0, 0, 0, 0
    avg_lat = sum(latencies) / len(latencies)
    min_lat = min(latencies)
    max_lat = max(latencies)
    jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0
    return avg_lat, min_lat, max_lat, jitter


def check_tcp_port(host, port, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    start = time.perf_counter()
    try:
        result = sock.connect_ex((host, port))
        latency = (time.perf_counter() - start) * 1000
        return result == 0, latency, None
    except socket.gaierror:
        return False, 0, "Erro de DNS"
    except socket.timeout:
        return False, 0, "Timeout"
    except Exception as e:
        return False, 0, str(e)
    finally:
        sock.close()


def print_summary(console_list, success_count, fail_count, latencies, start_run):
    total_time = time.time() - start_run
    total_attempts = success_count + fail_count
    if total_attempts == 0:
        return

    avg_lat, min_lat, max_lat, jitter = calculate_stats(latencies)
    success_rate = success_count / total_attempts * 100

    summary_title = "\n📊 [bold white]Resumo da Execução[/bold white]"
    summary_table = Table(show_header=False, box=None)
    summary_table.add_row(
        "Sucesso / Falha", f"[green]{success_count}🟢[/] / [red]{fail_count}🔴[/]"
    )
    summary_table.add_row("Taxa de Sucesso", f"[bold cyan]{success_rate:.2f}%[/]")
    summary_table.add_row(
        "Latência (Mín/Méd/Máx)",
        f"[bold]{min_lat:.2f} / {avg_lat:.2f} / {max_lat:.2f} ms[/]",
    )
    summary_table.add_row("Jitter (Variação)", f"[bold magenta]{jitter:.2f} ms[/]")
    summary_table.add_row("Tempo Total", f"{total_time:.2f}s")

    for c in console_list:
        c.print(summary_title)
        c.print(summary_table)


@click.command()
@click.argument("host")
@click.argument("port", type=int)
@click.option(
    "--count",
    "-c",
    default=0,
    type=int,
    help="Número de pings (0 para infinito).",
    show_default=True,
)
@click.option(
    "--interval", "-i", default=1.0, help="Intervalo (segundos).", show_default=True
)
@click.option(
    "--timeout", "-t", default=2.0, help="Timeout (segundos).", show_default=True
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Arquivo de log (Padrão: tcp_ping_HOST_PORTA.log).",
)  # Mudado para None
def main(host, port, count, interval, timeout, output):
    """TCP PING TOOL - Utilitário de teste de conectividade."""

    # 1. Caminho base do script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Define o caminho da pasta de LOGS (dentro da pasta do script)
    logs_dir = os.path.join(script_dir, "logs")

    # 3. CRIA A PASTA SE NÃO EXISTIR (Importante!)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # 4. Lógica de nome dinâmico
    if output is None:
        filename = f"tcp_ping_{host}_{port}.log"
    else:
        filename = output

    # 5. O caminho final agora aponta para DENTRO da pasta logs
    log_path = os.path.join(logs_dir, filename)

    success_count = 0
    fail_count = 0
    latencies = []
    start_run = time.time()
    current_attempt = 0

    try:
        # 4. Usar log_path no modo "a" (append) para manter histórico
        with open(log_path, "a", encoding="utf-8") as log_file:
            file_console = Console(file=log_file, record=True)
            consoles = [console, file_console]

            header = f"\n🚀 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Testando TCP: [bold green]{host}[/bold green]:[underline]{port}[/underline]"
            if count > 0:
                header += f" ({count} tentativas)"

            for c in consoles:
                c.print(header, style="bold cyan")

            first_attempt = True

            try:
                while True:
                    if count > 0 and current_attempt >= count:
                        break

                    current_attempt += 1
                    success, latency, error = check_tcp_port(host, port, timeout)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if success:
                        success_count += 1
                        latencies.append(latency)
                        status_text = "[bold green]ABERTA[/bold green]"
                        icon = "🟢"
                    else:
                        fail_count += 1
                        status_text = (
                            f"[bold red]FECHADA[/bold red] ({error or 'Erro'})"
                        )
                        icon = "🔴"

                    if first_attempt:
                        table = Table(show_header=True, header_style="bold cyan")
                        table.add_column("Timestamp", style="dim")
                        table.add_column("Host:Porta")
                        table.add_column("Status", justify="center")
                        table.add_column("Latência", justify="right")
                        table.add_row(
                            timestamp,
                            f"{host}:{port}",
                            status_text,
                            f"{latency:.2f}ms" if success else "-",
                        )
                        for c in consoles:
                            c.print(table)
                        first_attempt = False
                    else:
                        msg = f"{icon} {timestamp} | {host}:{port} | {status_text} | {latency:.2f}ms"
                        for c in consoles:
                            c.print(msg)

                    if count == 0 or current_attempt < count:
                        time.sleep(interval)

                print_summary(consoles, success_count, fail_count, latencies, start_run)

            except KeyboardInterrupt:
                print_summary(consoles, success_count, fail_count, latencies, start_run)

    except Exception as e:
        console.print(f"\n❌ Erro crítico: {e}", style="bold red")
    finally:
        # 5. Exibe o caminho real onde foi salvo
        console.print(
            f"\n💾 Log atualizado em: [bold underline]{log_path}[/bold underline]",
            style="bold cyan",
        )


if __name__ == "__main__":
    main()
