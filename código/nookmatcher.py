#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NookMatcher - leitura da entrada (demo simples).

Le o CSV de jogadores e imprime uma tabela com cada jogador e suas
preferencias. Sem recomendacao ainda.

  - Colunas localizadas pelo CABECALHO (a ordem nao importa); colunas extras
    sao ignoradas.
  - 'ID do jogador' é obrigatorio: linhas sem ID sao reportadas e puladas.
  - Campos vazios = "sem preferencia" (exibidos como '-').

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
    """Le o CSV de jogadores, localizando as colunas pelo cabecalho.

    Colunas extras sao ignoradas e linhas sem 'ID do jogador' sao reportadas
    e puladas, sem interromper o processamento das demais.

    Args:
        path (str): Caminho do arquivo CSV de jogadores.

    Returns:
        tuple[list[dict], list[str]]: A lista de jogadores (cada um um dict
        com as colunas de COLS) e a lista de mensagens de erro por linha
        invalida.

    Raises:
        ValueError: Se a coluna 'ID do jogador' estiver ausente no cabecalho.
    """
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
    """Imprime os jogadores como uma tabela de texto alinhada.

    Cada coluna e dimensionada pelo maior valor presente; celulas vazias sao
    exibidas como '-'.

    Args:
        players (list[dict]): Jogadores a exibir, conforme devolvido por
            load_players.
    """
    grid = [COLS] + [[(p[c] or "-") for c in COLS] for p in players]
    widths = [max(len(r[j]) for r in grid) for j in range(len(COLS))]

    def line(cells):
        """Formata uma linha da tabela com as colunas alinhadas.

        Args:
            cells (list[str]): Valores ja resolvidos para cada coluna.

        Returns:
            str: A linha formatada.
        """
        return " | ".join(c.ljust(widths[j]) for j, c in enumerate(cells))

    print(line(COLS))
    print("-+-".join("-" * w for w in widths))
    for p in players:
        print(line([(p[c] or "-") for c in COLS]))


def main(argv=None):
    """Ponto de entrada: le o CSV informado e imprime a tabela de jogadores.

    Args:
        argv (list[str] | None): Argumentos de linha de comando; None usa
            sys.argv.
    """
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
