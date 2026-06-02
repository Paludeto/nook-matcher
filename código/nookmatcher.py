#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NookMatcher - leitura da entrada
===============================================
Uso:
    python nookmatcher.py --input jogadores_exemplo.csv
"""

import argparse
import csv
import os
import sys

PLAYER_ID_COL = "ID do jogador"
COLS = [PLAYER_ID_COL, "Gender", "Personality", "Style 1", "Style 2",
        "Hobby", "Color 1", "Color 2", "Species"]


def load_players(path):
    """Le o CSV e devolve (lista_de_jogadores, lista_de_erros)."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        if PLAYER_ID_COL not in headers:
            raise ValueError(
                f"Coluna obrigatoria '{PLAYER_ID_COL}' ausente no cabecalho. "
                f"Cabecalho encontrado: {headers}")
        rows = list(reader)

    players, errors = [], []
    for i, row in enumerate(rows, start=2):   # linha 1 = cabecalho
        pid = (row.get(PLAYER_ID_COL) or "").strip()
        if not pid:
            errors.append(f"Linha {i}: sem '{PLAYER_ID_COL}' -> ignorada.")
            continue
        players.append({c: (row.get(c) or "").strip() for c in COLS})
    return players, errors


def print_table(players):
    """Imprime os jogadores como tabela alinhada (vazio = '-')."""
    grid = [COLS] + [[(p[c] or "-") for c in COLS] for p in players]
    widths = [max(len(r[j]) for r in grid) for j in range(len(COLS))]

    def line(cells):
        return " | ".join(c.ljust(widths[j]) for j, c in enumerate(cells))

    print(line(COLS))
    print("-+-".join("-" * w for w in widths))
    for p in players:
        print(line([(p[c] or "-") for c in COLS]))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="NookMatcher - leitura da entrada (tabela de jogadores)")
    parser.add_argument("--input", required=True, help="CSV de jogadores")
    args = parser.parse_args(argv)

    if not os.path.exists(args.input):
        sys.exit(f"Arquivo de entrada nao encontrado: {args.input}")

    players, errors = load_players(args.input)

    print()
    if errors:
        print("LINHAS COM ERRO (ignoradas):")
        for e in errors:
            print(f"  - {e}")
        print()

    print_table(players)
    print()
    print(f"{len(players)} jogador(es) lido(s), {len(errors)} linha(s) com erro.")


if __name__ == "__main__":
    main()