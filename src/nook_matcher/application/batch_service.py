"""Serviço de aplicação para recomendação em lote (H2).

Coordena o fluxo: itera os jogadores lidos pela Infraestrutura, delega o
ranqueamento ao Domínio e coleta os erros por linha sem interromper o
processamento dos demais jogadores válidos.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from nook_matcher.domain.recommender import KNNRecommender, Recommendation
from nook_matcher.infrastructure.player_source import PlayerProfileReader


@dataclass(frozen=True)
class PlayerResult:
    """Resultado do processamento de um jogador (ou linha inválida).

    Attributes:
        source_line (int): Linha de origem no arquivo de entrada.
        player_id (str): Identificador do jogador (vazio em caso de erro).
        recommendations (list[Recommendation]): Villagers recomendados.
        error (str | None): Mensagem de erro, quando a linha é inválida.
    """

    source_line: int
    player_id: str = ""
    recommendations: list[Recommendation] = field(default_factory=list)
    error: str | None = None


@dataclass(frozen=True)
class BatchResult:
    """Resultado agregado do processamento do lote.

    Attributes:
        results (list[PlayerResult]): Resultado de cada linha, na ordem
            de leitura (válidos e inválidos).
    """

    results: list[PlayerResult]

    @property
    def total_players(self) -> int:
        """Número de jogadores válidos processados.

        Returns:
            int: Quantidade de resultados sem erro.
        """
        return sum(1 for result in self.results if result.error is None)

    @property
    def total_errors(self) -> int:
        """Número de linhas reportadas com erro.

        Returns:
            int: Quantidade de resultados com erro.
        """
        return sum(1 for result in self.results if result.error is not None)


class BatchRecommendationService:
    """Orquestra a recomendação em lote para todos os jogadores."""

    def __init__(
        self,
        recommender: KNNRecommender,
        player_reader: PlayerProfileReader,
    ) -> None:
        """Inicializa o serviço com suas dependências.

        Args:
            recommender (KNNRecommender): Recomendador do Domínio.
            player_reader (PlayerProfileReader): Fonte de perfis.
        """
        self._recommender = recommender
        self._reader = player_reader

    def run(self, top_n: int) -> BatchResult:
        """Processa todos os jogadores e agrega os resultados.

        Args:
            top_n (int): Quantidade de recomendações por jogador.

        Returns:
            BatchResult: Resultado por linha e os totais do lote.
        """
        results: list[PlayerResult] = []
        for row in self._reader.read():
            if row.error or row.profile is None:
                results.append(
                    PlayerResult(
                        source_line=row.source_line,
                        error=row.error,
                    )
                )
                continue
            recommendations = self._recommender.recommend(row.profile, top_n)
            results.append(
                PlayerResult(
                    source_line=row.source_line,
                    player_id=row.profile.player_id,
                    recommendations=recommendations,
                )
            )
        return BatchResult(results)
