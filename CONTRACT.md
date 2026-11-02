# Transfer contract
Manifest specifies sha256 (lowercase hex), count (1–4096) and chunks as index plus base64 content. Each supplied chunk is at most 1 MiB. Use python cli.py input.json database.sqlite to retain chunks across runs. Reusing an index with different bytes fails. Supply fewer chunks to see missing indices. A verified assembly yields its bytes as base64 in the result.
