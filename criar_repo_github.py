# -*- coding: utf-8 -*-
"""
criar_repo_github.py
Cria o repositório 'microvideoOS' no GitHub via API REST e faz o push do código.

Como usar:
  1. Gere um token em: https://github.com/settings/tokens/new
     Marque a permissão: repo (Full control of private repositories)
  2. Execute: python criar_repo_github.py SEU_TOKEN_AQUI
"""

import sys
import json
import urllib.request
import urllib.error
import subprocess
import os

USUARIO = "joshuaas5"
REPO_NAME = "microvideoOS"
DESCRICAO = "Sistema de gerenciamento para oficinas de eletrônica - Python/CustomTkinter"
PRIVADO = False  # True = privado, False = público


def criar_repo(token):
    url = "https://api.github.com/user/repos"
    dados = json.dumps({
        "name": REPO_NAME,
        "description": DESCRICAO,
        "private": PRIVADO,
        "auto_init": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=dados,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "Python",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            resultado = json.loads(resp.read())
            return resultado.get("html_url"), resultado.get("clone_url")
    except urllib.error.HTTPError as e:
        corpo = json.loads(e.read())
        msg = corpo.get("message", "")
        if "already exists" in msg:
            print(f"[INFO] Repositório já existe! Usando URL existente.")
            return (
                f"https://github.com/{USUARIO}/{REPO_NAME}",
                f"https://github.com/{USUARIO}/{REPO_NAME}.git",
            )
        print(f"[ERRO] GitHub API: {msg}")
        sys.exit(1)


def push_codigo(clone_url, token):
    # Injeta token na URL para autenticação
    url_com_token = clone_url.replace("https://", f"https://{USUARIO}:{token}@")

    base = os.path.dirname(os.path.abspath(__file__))

    cmds = [
        ["git", "remote", "remove", "origin"],  # remove se já existir
        ["git", "remote", "add", "origin", url_com_token],
        ["git", "branch", "-M", "main"],
        ["git", "push", "-u", "origin", "main"],
    ]

    for cmd in cmds:
        try:
            result = subprocess.run(cmd, cwd=base, capture_output=True, text=True)
            if result.returncode != 0 and "fatal" in result.stderr.lower():
                # Ignora erro de "remote não existe" no remove
                if "remove" in cmd and "No such remote" in result.stderr:
                    continue
                print(f"[AVISO] {result.stderr.strip()}")
        except Exception as e:
            print(f"[AVISO] {e}")

    print("[OK] Push realizado!")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    token = sys.argv[1].strip()
    print(f"[→] Criando repositório '{REPO_NAME}' para @{USUARIO}...")
    html_url, clone_url = criar_repo(token)
    print(f"[✓] Repositório: {html_url}")

    print("[→] Fazendo push do código...")
    push_codigo(clone_url, token)

    print()
    print("=" * 50)
    print(f"  ✅ Tudo pronto!")
    print(f"  🔗 {html_url}")
    print("=" * 50)


if __name__ == "__main__":
    main()
