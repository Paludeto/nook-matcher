"""Construção das justificativas de recomendação (H1/H5).

Converte a contribuição por eixo de um ``ScoreResult`` em fatores
legíveis, ordenados por relevância. O corte por quantidade de fatores é
responsabilidade da camada de apresentação (config ``--max-factors``).
"""

from __future__ import annotations

from nook_matcher.domain.entities import (
    AXES,
    AXIS_LABELS,
    PlayerProfile,
    Villager,
)
from nook_matcher.domain.similarity import ScoreResult


class ExplanationBuilder:
    """Gera os fatores que explicam por que um villager foi recomendado."""

    def build(
        self,
        profile: PlayerProfile,
        villager: Villager,
        result: ScoreResult,
    ) -> list[str]:
        """Monta os fatores de justificativa em ordem de relevância.

        Args:
            profile (PlayerProfile): Perfil do jogador.
            villager (Villager): Villager recomendado.
            result (ScoreResult): Resultado da similaridade, usado para
                ordenar os eixos por contribuição.

        Returns:
            list[str]: Fatores no formato ``"Rótulo: valores"``, do mais
            ao menos relevante; vazio se nenhum eixo contribuiu.
        """
        contributing = [
            axis for axis, weight in result.per_axis.items() if weight > 0
        ]
        ordered = sorted(
            contributing,
            key=lambda axis: (-result.per_axis[axis], AXES.index(axis)),
        )
        factors: list[str] = []
        for axis in ordered:
            matched = self._matched_values(profile, villager, axis)
            if not matched:
                continue
            label = AXIS_LABELS.get(axis, axis)
            factors.append(f"{label}: {', '.join(matched)}")
        return factors

    @staticmethod
    def _matched_values(
        profile: PlayerProfile, villager: Villager, axis: str
    ) -> list[str]:
        """Lista os valores do villager que casam com a preferência.

        Args:
            profile (PlayerProfile): Perfil do jogador.
            villager (Villager): Villager recomendado.
            axis (str): Eixo avaliado.

        Returns:
            list[str]: Valores do villager (na grafia original) que
            coincidem com a preferência do jogador, em ordem alfabética.
        """
        prefs = {value.lower() for value in profile.axis_values(axis)}
        matched = [
            value
            for value in villager.axis_values(axis)
            if value.lower() in prefs
        ]
        return sorted(matched)
