"""Recomendador KNN baseado em similaridade categórica (Domínio).

Ranqueia villagers por compatibilidade com o perfil do jogador, anexando
a cada recomendação a sua justificativa (H1/H5). O ranqueamento é
determinístico: empates são resolvidos pelo nome e o caso sem
preferências usa uma seed fixa (H3/H4).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from nook_matcher.domain.entities import PlayerProfile, Villager
from nook_matcher.domain.explanation import ExplanationBuilder
from nook_matcher.domain.similarity import SimilarityStrategy

# Fator sinalizado quando o jogador não informa nenhuma preferência (H3).
_NO_PREFERENCE_FACTOR = "Nenhuma preferência informada — seleção aleatória"


@dataclass(frozen=True)
class Recommendation:
    """Um villager recomendado, com pontuação e justificativa.

    Attributes:
        villager (Villager): O villager recomendado.
        score (float): Compatibilidade em ``[0, 1]``.
        explanation (list[str]): Fatores que motivaram a recomendação,
            do mais ao menos relevante (H1/H5).
    """

    villager: Villager
    score: float
    explanation: list[str] = field(default_factory=list)


class KNNRecommender:
    """Recomenda villagers pelos vizinhos mais próximos do perfil."""

    def __init__(
        self,
        strategy: SimilarityStrategy,
        villagers: list[Villager],
        seed: int = 42,
        explanation_builder: ExplanationBuilder | None = None,
    ) -> None:
        """Inicializa o recomendador.

        Args:
            strategy (SimilarityStrategy): Métrica de similaridade.
            villagers (list[Villager]): Catálogo de villagers candidatos.
            seed (int): Seed para os componentes aleatórios (H4).
            explanation_builder (ExplanationBuilder | None): Construtor de
                justificativas; ``None`` usa o padrão.
        """
        self._strategy = strategy
        self._villagers = list(villagers)
        self._seed = seed
        self._explainer = explanation_builder or ExplanationBuilder()

    def recommend(
        self, profile: PlayerProfile, top_n: int
    ) -> list[Recommendation]:
        """Ranqueia villagers por compatibilidade, em ordem decrescente.

        Args:
            profile (PlayerProfile): Perfil do jogador; eixos podem estar
                vazios.
            top_n (int): Quantidade de recomendações a retornar.

        Returns:
            list[Recommendation]: Os ``top_n`` villagers mais compatíveis,
            em ordem decrescente de compatibilidade.

        Raises:
            ValueError: Se ``top_n`` for menor ou igual a zero.
        """
        if top_n <= 0:
            raise ValueError("top_n deve ser maior que zero.")
        if not profile.has_preferences():
            return self._random_recommendations(top_n)

        scored: list[tuple[float, str, Villager, list[str]]] = []
        for villager in self._villagers:
            result = self._strategy.score(profile, villager)
            factors = self._explainer.build(profile, villager, result)
            scored.append((result.value, villager.name, villager, factors))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [
            Recommendation(villager, value, factors)
            for value, _name, villager, factors in scored[:top_n]
        ]

    def _random_recommendations(self, top_n: int) -> list[Recommendation]:
        """Sorteia villagers quando não há nenhuma preferência (H3).

        A amostragem usa a seed fixa sobre o catálogo ordenado por nome,
        garantindo resultados idênticos entre execuções (H4).

        Args:
            top_n (int): Quantidade de recomendações a retornar.

        Returns:
            list[Recommendation]: Villagers sorteados, cada um sinalizando
            que nenhuma preferência foi utilizada.
        """
        pool = sorted(self._villagers, key=lambda villager: villager.name)
        if not pool:
            return []
        rng = random.Random(self._seed)
        chosen = rng.sample(pool, min(top_n, len(pool)))
        return [
            Recommendation(villager, 0.0, [_NO_PREFERENCE_FACTOR])
            for villager in chosen
        ]
