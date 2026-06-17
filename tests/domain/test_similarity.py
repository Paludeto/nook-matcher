"""Testes para nook_matcher.domain.similarity.

Estratégia de teste
-------------------
Os testes cobrem ``_axis_overlap`` e ``WeightedOverlapSimilarity.score``,
as duas funções principais do cálculo de compatibilidade. Como nenhuma delas
acessa arquivos ou banco de dados, não é necessário usar mocks — basta
criar perfis e villagers diretamente. Cada função tem três tipos de caso:
*sucesso* (entrada normal com resultado positivo), *falha* (entrada válida
que deve retornar zero) e *borda* (situações menos óbvias, como preferência
vazia, texto em caixa diferente e sobreposição parcial de cores). Lacunas:
``CosineSimilarity``, ``KNNRecommender``, a leitura de CSV e a CLI não são
cobertas por estes testes.
"""

import pytest

from nook_matcher.domain.entities import PlayerProfile, Villager
from nook_matcher.domain.similarity import (
    ScoreResult,
    WeightedOverlapSimilarity,
    _axis_overlap,
)


# ---------------------------------------------------------------------------
# Fixtures auxiliares
# ---------------------------------------------------------------------------

def _player(**kwargs) -> PlayerProfile:
    defaults = dict(
        player_id="p1",
        personality="",
        species="",
        hobby="",
        colors=(),
        styles=(),
    )
    defaults.update(kwargs)
    return PlayerProfile(**defaults)


def _villager(**kwargs) -> Villager:
    defaults = dict(
        name="Tom",
        species="Cat",
        personality="Lazy",
        hobby="Education",
        birthday="1/1",
        color_1="Red",
        color_2="",
        style_1="Cool",
        style_2="",
    )
    defaults.update(kwargs)
    return Villager(**defaults)


# ---------------------------------------------------------------------------
# _axis_overlap
# ---------------------------------------------------------------------------

class TestAxisOverlap:
    """Testes para a função _axis_overlap."""

    def test_single_value_full_match_returns_one(self):
        """Sucesso: eixo com um valor e correspondência total → 1.0."""
        profile = _player(personality="Peppy")
        villager = _villager(personality="Peppy")
        assert _axis_overlap(profile, villager, "personality") == pytest.approx(1.0)

    def test_single_value_no_match_returns_zero(self):
        """Falha: preferência preenchida mas villager diverge → 0.0."""
        profile = _player(personality="Peppy")
        villager = _villager(personality="Lazy")
        assert _axis_overlap(profile, villager, "personality") == pytest.approx(0.0)

    def test_empty_preference_returns_zero(self):
        """Borda: jogador sem preferência no eixo → 0.0 (não penaliza)."""
        profile = _player(personality="")
        villager = _villager(personality="Peppy")
        assert _axis_overlap(profile, villager, "personality") == pytest.approx(0.0)

    def test_case_insensitive_match(self):
        """Borda: diferença de caixa não impede correspondência."""
        profile = _player(personality="PEPPY")
        villager = _villager(personality="peppy")
        assert _axis_overlap(profile, villager, "personality") == pytest.approx(1.0)

    def test_partial_multi_value_overlap(self):
        """Borda: 1 de 2 cores em comum → sobreposição de 0.5."""
        profile = _player(colors=("Red", "Blue"))
        villager = _villager(color_1="Red", color_2="Green")
        assert _axis_overlap(profile, villager, "color") == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# WeightedOverlapSimilarity.score
# ---------------------------------------------------------------------------

class TestWeightedOverlapSimilarity:
    """Testes para WeightedOverlapSimilarity.score."""

    def setup_method(self):
        self.strategy = WeightedOverlapSimilarity()

    def test_single_axis_full_match_score_is_one(self):
        """Sucesso: único eixo preenchido com correspondência total → 1.0."""
        profile = _player(personality="Peppy")
        villager = _villager(personality="Peppy")
        result = self.strategy.score(profile, villager)
        assert result.value == pytest.approx(1.0)
        assert "personality" in result.per_axis

    def test_filled_axis_no_match_value_is_zero(self):
        """Falha: eixo preenchido sem correspondência → value 0.0, chave presente."""
        profile = _player(personality="Peppy")
        villager = _villager(personality="Lazy")
        result = self.strategy.score(profile, villager)
        assert result.value == pytest.approx(0.0)
        assert result.per_axis.get("personality") == pytest.approx(0.0)

    def test_empty_profile_returns_zero_scoreresult(self):
        """Borda: perfil sem nenhuma preferência → ScoreResult(0.0, {})."""
        profile = _player()
        villager = _villager(personality="Peppy")
        assert self.strategy.score(profile, villager) == ScoreResult(0.0, {})

    def test_all_axes_full_match_score_is_one(self):
        """Borda: todos os eixos preenchidos e correspondidos → 1.0."""
        profile = _player(
            personality="Peppy",
            species="Cat",
            hobby="Education",
            colors=("Red",),
            styles=("Cool",),
        )
        villager = _villager(
            personality="Peppy",
            species="Cat",
            hobby="Education",
            color_1="Red",
            style_1="Cool",
        )
        result = self.strategy.score(profile, villager)
        assert result.value == pytest.approx(1.0)

    def test_custom_weights_change_score(self):
        """Borda: pesos customizados alteram o valor do score calculado."""
        # Jogador com personalidade (match) e espécie (sem match).
        profile = _player(personality="Peppy", species="Cat")
        villager = _villager(personality="Peppy", species="Dog")

        # Pesos padrão: personality=1.5, species=1.0 → total=2.5
        default_result = WeightedOverlapSimilarity().score(profile, villager)
        assert default_result.value == pytest.approx(1.5 / 2.5)

        # Pesos iguais: personality=1.0, species=1.0 → total=2.0
        equal_result = WeightedOverlapSimilarity(
            weights={"personality": 1.0, "species": 1.0}
        ).score(profile, villager)
        assert equal_result.value == pytest.approx(1.0 / 2.0)
