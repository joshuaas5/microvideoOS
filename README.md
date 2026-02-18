# 🔧 Sistema Oficina 2026

Sistema de gerenciamento para oficinas de eletrônica. Substitui software legado de 30 anos por um executável único (.exe), moderno, robusto e 100% offline.

## Stack

| Tecnologia | Uso |
|---|---|
| Python 3.10+ | Linguagem principal |
| CustomTkinter | Interface gráfica (Dark/Light) |
| SQLite3 | Banco de dados local (`oficina.db`) |
| ReportLab | Geração de PDF (Ordem de Serviço) |
| PyInstaller | Build para `.exe` |

## Estrutura

```
microvideoOS/
├── main.py            # Interface gráfica principal
├── database.py        # Conexão e CRUD SQLite
├── print_engine.py    # Geração de PDF (duas vias)
├── backup.py          # Backup automático
├── migrador.py        # Importação de CSV legado
├── requirements.txt
└── README.md
```

## Como Usar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```

## Build (.exe)

```bash
pyinstaller --onefile --windowed --name="Oficina2026" main.py
```

## Funcionalidades

- ✅ Cadastro de clientes e ordens de serviço (OS)
- ✅ Geração automática de RA (Ano + Sequencial)
- ✅ Impressão de OS em PDF (Via Loja + Via Cliente)
- ✅ Dashboard com contadores de status
- ✅ Busca de clientes "as-you-type"
- ✅ Backup automático com rotação de 30 dias
- ✅ Migração de dados CSV do sistema antigo
- ✅ Tema Dark/Light alternável
- ✅ Interface amigável para usuários idosos (fontes grandes, alto contraste)
