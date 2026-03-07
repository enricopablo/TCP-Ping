# 🚀 TCP Ping Tool (Python + UV)

Uma ferramenta de linha de comando (CLI) robusta para testar a conectividade de portas **TCP**. Diferente do ping tradicional (ICMP), esta ferramenta valida se serviços específicos (Web, SSH, Banco de Dados, etc.) estão aceitando conexões, fornecendo métricas de latência, estabilidade e histórico automatizado.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![UV](https://img.shields.io/badge/Managed%20by-UV-purple?logo=python)
![OS](https://img.shields.io/badge/OS-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

## ✨ Funcionalidades

* **Handshake TCP:** Mede o tempo de resposta real da aplicação (SYN/SYN-ACK).
* **Estatísticas Avançadas:** Média, Mínimo, Máximo e **Jitter** (variação da latência).
* **Modo Contagem (`-c`):** Defina um limite de disparos ou rode infinitamente.
* **Organização Automática de Logs:** Logs centralizados na pasta `/logs` com nomes dinâmicos por Host e Porta.
* **Modo Histórico (Append):** Preserva testes anteriores no mesmo arquivo de log para consultas futuras.
* **Interface Rica:** Utiliza a biblioteca `Rich` para tabelas e cores no terminal.

---

## 🛠️ Pré-requisitos

O único requisito é o `uv` (gerenciador de pacotes Python ultra-rápido).

**macOS / Linux:**
```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
```
Ou via `pip`:

```bash
pip install uv
```

**Windows (PowerShell):**

```bash
powershell -c "iwr [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
```

Ou via `pip`:

```bash
pip install uv
```

## 🚀 Como Executar

O `uv` gerencia as dependências automaticamente a partir do cabeçalho do script.

```bash
uv run main.py <host> <porta> [opções]
```

Exemplos:

```bash
# Teste básico (roda até você apertar Ctrl+C)
uv run main.py google.com 443

# 10 tentativas com intervalo de 0.5s
uv run main.py 1.1.1.1 80 -c 10 -i 0.5
```

## 📂 Estrutura do Projeto

O script organiza-se automaticamente para manter a raiz limpa:

```bash
.
├── main.py          # Script principal
├── README.md        # Documentação
├── pyproject.toml   # Configurações do projeto UV
├── uv.lock          # Trava de versões de dependências
└── logs/            # Pasta criada automaticamente
    ├── tcp_ping_1.1.1.1_80.log
    └── tcp_ping_8.8.8.8_80.log

```

## ⚡ Configurando o Atalho (tping)

Para rodar de qualquer lugar do terminal apenas digitando `tping`:

🍎 macOS e 🐧 Linux (Zsh/Bash)
Adicione ao seu `~/.zshrc` ou `~/.bashrc`:

```bash
alias tping='uv run /CAMINHO/COMPLETO/PARA/main.py'
```

🪟 Windows (PowerShell)
Adicione ao seu `$PROFILE`:

1. Abra o terminal do `PowerShell` e force um novo `$PROFILE`:
```bash
New-Item $PROFILE -Force
```

2. Ainda no temrinal do `PowerShell` digite:
```bash
notepad $PROFILE
```
3. No aquivo que for aberto crie o `alias`:
```bash
function tping { uv run "C:\CAMINHO\PARA\main.py" @args }
```

## 📊 Opções da CLI

```bash
Opção       Atalho  Descrição                                   Padrão
--count     -c      Número de pings (0 para infinito)           0
--interval  -i      Intervalo entre pings (segundos)            1.0
--timeout   -t      Tempo limite de espera (segundos)           2.0
--output    -o      Nome customizado do log (dentro de /logs)   Dinâmico
```

### 🔍 Entendendo a Saída

Ao executar o `tping`, a ferramenta realiza o **Three-Way Handshake do TCP**. A latência exibida é o tempo decorrido entre o envio do `SYN` e o recebimento do `SYN-ACK`.

- 🟢 ABERTA: O serviço respondeu e a conexão foi aceita.

- 🔴 FECHADA: Conexão recusada ou timeout (firewall bloqueando).

- Jitter: Variação na latência. Valores altos indicam instabilidade na rota ou sobrecarga no host.

---
