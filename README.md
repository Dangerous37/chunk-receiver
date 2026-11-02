# Chunk Receiver

Resume an interrupted local file transfer by querying durable chunk receipts. Store content and its index in one transaction and release the assembled file only after digest verification.

## Run locally

Use Python 3.12. The project uses the standard library. From the repository root:

```sh
python cli.py example.json
python -m unittest -v
```

The included example is synthetic. Pass a different UTF-8 JSON file to inspect your own input. The command prints JSON to stdout. Invalid input returns status 2 and an explanation on stderr. See [CONTRACT.md](CONTRACT.md) for input fields and interpretation.

## Operational limits

Local staging adapter, not an internet upload service. Trusted bounded input. Assembly is in memory; intended for small files. Stored chunks are retained. The entire batch is rolled back if an index conflicts.

## Resumen en español

Guarda bloques de forma persistente y reconstruye un archivo únicamente al verificar su hash completo.
