"""Estratégias de similaridade do NookMatcher (padrão Strategy).

Cada métrica encapsula uma forma de medir a compatibilidade entre um
perfil e um villager, podendo ser trocada sem alterar o
``KNNRecommender``. A variante ponderada expõe a contribuição por eixo,
que alimenta as justificativas (H1/H5).
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

from nook_matcher.domain.entities import PlayerProfile, Villager

# Pesos padrão por eixo: personalidade e tema (cor) são os eixos
# dominantes na elicitação, por isso recebem peso maior.
_DEFAULT_WEIGHTS: dict[str, float] = {
    "personality": 1.5,
    "species": 1.0,
    "hobby": 1.0,
    "color": 1.5,
    "style": 1.0,
}


@dataclass(frozen=True)
class ScoreResult:
    """Resultado de uma comparação perfil×villager.

    Attributes:
        value (float): Compatibilidade global em ``[0, 1]``.
        per_axis (dict[str, float]): Contribuição de cada eixo para
            ``value``; as parcelas somam ``value``.
    """

    value: float
    per_axis: dict[str, float]


def _axis_overlap(
    profile: PlayerProfile, villager: Villager, axis: str
) -> float:
    """Calcula a fração das preferências do jogador atendida em um eixo.

    A comparação é insensível a maiúsculas/minúsculas. Para eixos com
    múltiplos valores (cor, estilo), o resultado é a proporção de valores
    em comum (ex.: 1 de 2 cores casadas resulta em ``0.5``).

    Args:
        profile (PlayerProfile): Perfil do jogador.
        villager (Villager): Villager candidato.
        axis (str): Nome do eixo avaliado.

    Returns:
        float: Sobreposição em ``[0, 1]``; ``0.0`` se o jogador não
        informou preferência naquele eixo.
    """
    prefs = {value.lower() for value in profile.axis_values(axis)}
    if not prefs:
        return 0.0
    values = {value.lower() for value in villager.axis_values(axis)}
    return len(prefs & values) / len(prefs)


class SimilarityStrategy(ABC):
    """Contrato comum às métricas de similaridade (padrão Strategy)."""

    @abstractmethod
    def score(self, profile: PlayerProfile, villager: Villager) -> ScoreResult:
        """Calcula a compatibilidade entre um perfil e um villager.

        Args:
            profile (PlayerProfile): Perfil do jogador.
            villager (Villager): Villager candidato.

        Returns:
            ScoreResult: Compatibilidade global e contribuição por eixo.
        """


class WeightedOverlapSimilarity(SimilarityStrategy):
    """Sobreposição categórica ponderada sobre os eixos preenchidos.

    Considera apenas os eixos para os quais o jogador informou
    preferência (H3), normalizando pela soma dos pesos desses eixos para
    manter o resultado em ``[0, 1]``.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        """Inicializa a estratégia com os pesos por eixo.

        Args:
            weights (dict[str, float] | None): Pesos por eixo; ``None``
                usa os pesos padrão.
        """
        self.weights = dict(weights) if weights else dict(_DEFAULT_WEIGHTS)

    def score(self, profile: PlayerProfile, villager: Villager) -> ScoreResult:
        filled = profile.filled_axes()
        if not filled:
            return ScoreResult(0.0, {})
        total_weight = sum(self.weights.get(a, 1.0) for a in filled)
        if total_weight <= 0:
            return ScoreResult(0.0, {a: 0.0 for a in filled})
        per_axis: dict[str, float] = {}
        for axis in filled:
            weight = self.weights.get(axis, 1.0)
            overlap = _axis_overlap(profile, villager, axis)
            per_axis[axis] = weight * overlap / total_weight
        return ScoreResult(sum(per_axis.values()), per_axis)


class CosineSimilarity(SimilarityStrategy):
    """Similaridade do cosseno sobre vetores categóricos one-hot.

    As preferências do jogador e os atributos do villager são tratados
    como vetores binários sobre os pares ``(eixo, valor)`` dos eixos
    preenchidos (H3). O resultado permanece em ``[0, 1]``.
    """

    def score(self, profile: PlayerProfile, villager: Villager) -> ScoreResult:
        filled = profile.filled_axes()
        if not filled:
            return ScoreResult(0.0, {})
        profile_size = 0
        villager_size = 0
        shared: dict[str, int] = {}
        for axis in filled:
            prefs = {value.lower() for value in profile.axis_values(axis)}
            values = {value.lower() for value in villager.axis_values(axis)}
            profile_size += len(prefs)
            villager_size += len(values)
            shared[axis] = len(prefs & values)
        if profile_size == 0 or villager_size == 0:
            return ScoreResult(0.0, {a: 0.0 for a in filled})
        denom = math.sqrt(profile_size) * math.sqrt(villager_size)
        per_axis = {a: shared[a] / denom for a in filled}
        return ScoreResult(sum(per_axis.values()), per_axis)
