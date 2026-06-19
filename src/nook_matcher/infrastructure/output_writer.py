"""Exportação das recomendações para CSV (Infraestrutura).

Escreve um arquivo CSV com uma linha por par jogador×villager,
associando cada jogador às suas recomendações (H2). As linhas inválidas
do lote não entram no arquivo; elas continuam sendo reportadas pela
camada de apresentação.
"""

from __future__ import annotations

import csv
from pathlib import Path

from nook_matcher.application.batch_service import BatchResult
from nook_matcher.domain.recommender import Recommendation

# Cabeçalho do CSV de saída, em pt-BR para refletir os rótulos exibidos.
_HEADER = [
    "jogador",
    "posicao",
    "villager",
    "compatibilidade",
    "especie",
    "personalidade",
    "hobby",
    "cor",
    "aniversario",
    "fatores",
]


class CsvRecommendationWriter:
    """Grava o resultado do lote em um arquivo CSV."""

    def __init__(self, path: str | Path, max_factors: int = 3) -> None:
        """Inicializa o exportador.

        Args:
            path (str | Path): Caminho do arquivo CSV de saída.
            max_factors (int): Número máximo de fatores por villager,
                consistente com a exibição no terminal (H5).
        """
        self.path = Path(path)
        self.max_factors = max_factors

    def write(self, batch_result: BatchResult) -> Path:
        """Escreve as recomendações no CSV, criando a pasta se preciso.

        Args:
            batch_result (BatchResult): Resultado do processamento.

        Returns:
            Path: Caminho do arquivo efetivamente escrito.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(_HEADER)
            for player in batch_result.results:
                if player.error is not None:
                    continue
                for rank, rec in enumerate(player.recommendations, start=1):
                    writer.writerow(self._row(player.player_id, rank, rec))
        return self.path

    def _row(
        self, player_id: str, rank: int, rec: Recommendation
    ) -> list[str]:
        """Monta a linha do CSV para uma recomendação.

        Args:
            player_id (str): Identificador do jogador.
            rank (int): Posição da recomendação (1-indexada).
            rec (Recommendation): Recomendação a serializar.

        Returns:
            list[str]: Valores da linha, na ordem de :data:`_HEADER`.
        """
        villager = rec.villager
        factors = rec.explanation[: self.max_factors]
        factors_str = (
            "; ".join(factors) if factors else "sem fatores identificados"
        )
        return [
            player_id,
            str(rank),
            villager.name,
            f"{rec.score * 100:.1f}%",
            villager.species,
            villager.personality,
            villager.hobby,
            villager.color,
            villager.birthday or "—",
            factors_str,
        ]


class JsonRecommendationWriter:
    """Grava o resultado do lote em um arquivo JSON."""

    def __init__(self, path: str | Path, max_factors: int = 3) -> None:
        """Inicializa o exportador.

        Args:
            path (str | Path): Caminho do arquivo JSON de saída.
            max_factors (int): Número máximo de fatores por villager,
                consistente com a exibição no terminal (H5).
        """
        self.path = Path(path)
        self.max_factors = max_factors

    def write(self, batch_result: BatchResult) -> Path:
        """Escreve as recomendações no JSON, criando a pasta se preciso.

        Args:
            batch_result (BatchResult): Resultado do processamento.

        Returns:
            Path: Caminho do arquivo efetivamente escrito.
        """
        import json

        self.path.parent.mkdir(parents=True, exist_ok=True)
        output_data = []
        for player in batch_result.results:
            if player.error is not None:
                continue
            player_recs = []
            for rank, rec in enumerate(player.recommendations, start=1):
                villager = rec.villager
                factors = rec.explanation[: self.max_factors]
                player_recs.append(
                    {
                        "posicao": rank,
                        "villager": villager.name,
                        "compatibilidade": f"{rec.score * 100:.1f}%",
                        "especie": villager.species,
                        "personalidade": villager.personality,
                        "hobby": villager.hobby,
                        "cor": villager.color,
                        "aniversario": villager.birthday or "—",
                        "fatores": factors,
                    }
                )
            output_data.append(
                {
                    "jogador": player.player_id,
                    "recomendacoes": player_recs,
                }
            )

        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(output_data, handle, ensure_ascii=False, indent=2)

        return self.path
