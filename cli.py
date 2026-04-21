#!/usr/bin/env python3
# cli.py
# Einfaches Mining-CLI für "Sovereign"
# Verwendung:
#   python cli.py mine
#
# Verhalten:
# - Proof-of-Work mit SHA-256
# - Difficulty: 4 (d.h. Hash muss mit vier Nullen beginnen)
# - Reward pro gefundenem Block: 50 SVN
# - Einfache lokale Balance in balance.txt (wird erstellt/aktualisiert)
#
# Hinweis: Dieses Skript ist zu Demonstrationszwecken; kein echtes Krypto-Produkt.

import argparse
import hashlib
import json
import os
import time
from datetime import datetime

# Mining-Parameter
DIFFICULTY = 4             # Anzahl führender Nullen
REWARD = 50                # Reward in SVN pro Block
BALANCE_FILE = "balance.txt"  # Datei, in der die Balance lokal gespeichert wird

# Hilfsfunktion: liest Balance aus der Datei (falls vorhanden)
def read_balance():
    if not os.path.exists(BALANCE_FILE):
        return 0
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0

# Hilfsfunktion: schreibt Balance in die Datei
def write_balance(bal):
    with open(BALANCE_FILE, "w", encoding="utf-8") as f:
        f.write(str(int(bal)))

# Erzeugt einen SHA-256 Hash aus Blockdaten (als deterministische Zeichenkette)
def hash_block(block_dict, nonce):
    # Wir serialisieren das Dictionary sortiert für deterministische Hash-Berechnung
    block_string = json.dumps(block_dict, sort_keys=True, separators=(',', ':'))
    # Füge den Nonce an
    candidate = f"{block_string}|{nonce}"
    # Berechne SHA-256 Hexdigest
    return hashlib.sha256(candidate.encode("utf-8")).hexdigest()

# Mining-Funktion: versucht, einen gültigen Nonce zu finden
def mine_block(index=0, prev_hash="0"*64, data="Sovereign block"):
    # Erstelle ein Block-Template
    block = {
        "index": index,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "prev_hash": prev_hash,
        "data": data,
    }
    target_prefix = "0" * DIFFICULTY
    nonce = 0
    start = time.time()
    # Endlosschleife bis ein Hash mit required prefix gefunden wird
    while True:
        h = hash_block(block, nonce)
        if h.startswith(target_prefix):
            elapsed = time.time() - start
            # Gefundener Block (vereinfachtes Format)
            found_block = {
                "index": index,
                "timestamp": block["timestamp"],
                "nonce": nonce,
                "hash": h,
                "prev_hash": prev_hash,
                "data": data,
                "elapsed_s": elapsed,
            }
            return found_block
        nonce += 1

# CLI Entrypoint
def main():
    parser = argparse.ArgumentParser(description="Sovereign CLI - einfaches Mining Demo")
    sub = parser.add_subparsers(dest="command", required=True)

    # Mine-Subcommand
    mine_parser = sub.add_parser("mine", help="Starte Mining (ein Block)")
    mine_parser.add_argument("--data", help="Block-Daten (default 'Sovereign block')", default="Sovereign block")
    mine_parser.add_argument("--start-index", help="Start-Index des Blocks (default 0)", type=int, default=0)
    mine_parser.add_argument("--prev-hash", help="Vorheriger Hash (default 64x '0')", default="0"*64)

    args = parser.parse_args()

    if args.command == "mine":
        # Informiere über Parameter
        print(f"Mining: difficulty={DIFFICULTY}, reward={REWARD} SVN")
        # Starte Mining (ein Block)
        found = mine_block(index=args.start_index, prev_hash=args.prev_hash, data=args.data)
        # Aktualisiere Balance
        balance = read_balance()
        balance += REWARD
        write_balance(balance)
        # Ausgabe wie gewünscht (Deutsch)
        print(f"Block gefunden! Balance: {balance} SVN")
        # Zusätzliche Details (optional, kommentiert)
        # print(json.dumps(found, indent=2))  # Bei Bedarf auskommentieren, um Blockdetails zu sehen.

if __name__ == "__main__":
    main()