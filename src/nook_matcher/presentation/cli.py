#!/usr/bin/env python3
"""Ponto de entrada da linha de comando para o NookMatcher."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from nook_matcher.application.batch_service import (
    BatchRecommendationService,
)
from nook_matcher.domain.recommender import KNNRecommender
from nook_matcher.domain.similarity import WeightedOverlapSimilarity
from nook_matcher.infrastructure.output_writer import (
    CsvRecommendationWriter,
)
from nook_matcher.infrastructure.player_source import (
    CsvPlayerProfileReader,
)
from nook_matcher.infrastructure.repositories import (
    CsvVillagerRepository,
)

_DEFAULT_TOP_N = 10
_DEFAULT_SEED = 42
_DEFAULT_MAX_FACTORS = 3
_DEFAULT_OUTPUT_DIR = "output"
_DEFAULT_VILLAGERS = Path(__file__).parents[3] / "data" / "villagers.csv"


def _build_parser() -> argparse.ArgumentParser:
    """Constrói e retorna o parser de argumentos da CLI.

    Returns:
        argparse.ArgumentParser: Parser configurado com todos os
        argumentos aceitos pelo NookMatcher.
    """
    parser = argparse.ArgumentParser(
        prog="nookmatcher",
        description=(
            "NookMatcher — recomendação de villagers para "
            "Animal Crossing: New Horizons."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="JOGADORES_CSV",
        help="CSV com perfis dos jogadores.",
    )
    parser.add_argument(
        "--villagers",
        default=str(_DEFAULT_VILLAGERS),
        metavar="VILLAGERS_CSV",
        help=f"CSV com dados dos villagers (padrão: {_DEFAULT_VILLAGERS}).",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=_DEFAULT_TOP_N,
        metavar="N",
        help=(
            "Quantidade de recomendações por jogador "
            f"(padrão: {_DEFAULT_TOP_N})."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=_DEFAULT_SEED,
        metavar="SEED",
        help=f"Seed para determinismo (padrão: {_DEFAULT_SEED}).",
    )
    parser.add_argument(
        "--max-factors",
        type=int,
        default=_DEFAULT_MAX_FACTORS,
        metavar="K",
        help=(
            "Número de fatores exibidos na justificativa "
            f"(padrão: {_DEFAULT_MAX_FACTORS})."
        ),
    )
    parser.add_argument(
        "--output",
        metavar="CSV",
        help=(
            "Caminho do CSV de saída. Se omitido, gera "
            f"{_DEFAULT_OUTPUT_DIR}/recomendacoes_<timestamp>.csv."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=_DEFAULT_OUTPUT_DIR,
        metavar="DIR",
        help=(
            "Pasta do CSV quando --output não é informado "
            f"(padrão: {_DEFAULT_OUTPUT_DIR})."
        ),
    )
    return parser


def _resolve_output_path(args: argparse.Namespace) -> Path:
    """Determina o caminho do CSV de saída a partir dos argumentos.

    Usa ``--output`` quando informado; caso contrário, gera um nome com
    timestamp dentro de ``--output-dir`` para preservar execuções
    anteriores.

    Args:
        args (argparse.Namespace): Argumentos já parseados.

    Returns:
        Path: Caminho do arquivo CSV a ser escrito.
    """
    if args.output:
        return Path(args.output)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(args.output_dir) / f"recomendacoes_{timestamp}.csv"


def _format_recommendation(rank: int, rec, max_factors: int) -> str:
    """Formata uma recomendação individual para exibição no terminal.

    Args:
        rank (int): Posição na lista (1-indexada).
        rec (Recommendation): Recomendação produzida pelo domínio.
        max_factors (int): Número máximo de fatores de justificativa.

    Returns:
        str: Bloco de texto formatado para a recomendação.
    """
    v = rec.villager
    pct = f"{rec.score * 100:.1f}%"
    factors = rec.explanation[:max_factors]
    factors_str = (
        ", ".join(factors) if factors else "sem fatores identificados"
    )
    birthday = v.birthday or "—"
    return (
        f"  {rank:>2}. {v.name} ({pct})\n"
        f"      Espécie: {v.species} | "
        f"Personalidade: {v.personality} | "
        f"Hobby: {v.hobby}\n"
        f"      Cor: {v.color} | Aniversário: {birthday}\n"
        f"      Fatores: {factors_str}"
    )


def _print_batch_result(batch_result, max_factors: int) -> None:
    """Exibe o resultado do processamento batch no stdout.

    Itera sobre todos os resultados: imprime recomendações para jogadores
    válidos e reporta o erro para linhas inválidas, sem interromper a
    exibição dos demais (H2).

    Args:
        batch_result (BatchResult): Resultado devolvido pelo serviço.
        max_factors (int): Número máximo de fatores a exibir por villager.
    """
    for player_result in batch_result.results:
        if player_result.error:
            print(
                f"\n[ERRO] {player_result.source_line}: "
                f"{player_result.error}"
            )
            continue

        print(f"\nJogador: {player_result.player_id}")
        print("-" * 40)
        for rank, rec in enumerate(player_result.recommendations, start=1):
            print(_format_recommendation(rank, rec, max_factors))

    total = batch_result.total_players
    errors = batch_result.total_errors
    print(
        f"\n{total} jogador(es) processado(s), " f"{errors} linha(s) com erro."
    )


def main(argv: list[str] | None = None) -> None:
    """Ponto de entrada da CLI: parseia argumentos e executa o caso de uso.

    Valida os caminhos informados, monta o grafo de dependências
    (repositórios, estratégia de similaridade, recommender e serviço
    batch) e delega a execução ao serviço de aplicação, exibindo os
    resultados formatados no stdout.

    Args:
        argv (list[str] | None): Argumentos de linha de comando; None usa
            sys.argv.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    villagers_path = Path(args.villagers)

    if not input_path.exists():
        sys.exit(f"Arquivo de entrada não encontrado: {input_path}")
    if not villagers_path.exists():
        sys.exit(f"Arquivo de villagers não encontrado: {villagers_path}")
    if args.top_n <= 0:
        sys.exit("--top-n deve ser maior que zero.")

    villager_repo = CsvVillagerRepository(villagers_path)
    player_reader = CsvPlayerProfileReader(input_path)
    strategy = WeightedOverlapSimilarity()
    recommender = KNNRecommender(
        strategy=strategy,
        villagers=villager_repo.load_all(),
        seed=args.seed,
    )
    service = BatchRecommendationService(
        recommender=recommender,
        player_reader=player_reader,
    )

    batch_result = service.run(top_n=args.top_n)
    _print_batch_result(batch_result, max_factors=args.max_factors)

    output_path = _resolve_output_path(args)
    writer = CsvRecommendationWriter(output_path, max_factors=args.max_factors)
    written = writer.write(batch_result)
    print(f"\nRecomendações exportadas para: {written}")


if __name__ == "__main__":
    main()
