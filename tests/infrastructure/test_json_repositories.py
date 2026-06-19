"""Testes para os repositórios, leitores e escritores de JSON."""

import json
from pathlib import Path
import pytest

from nook_matcher.domain.entities import Villager, PlayerProfile
from nook_matcher.infrastructure.repositories import JsonVillagerRepository
from nook_matcher.infrastructure.player_source import JsonPlayerProfileReader
from nook_matcher.infrastructure.output_writer import JsonRecommendationWriter
from nook_matcher.application.batch_service import BatchResult, PlayerResult
from nook_matcher.domain.recommender import Recommendation


def test_json_villager_repository_loads_correctly(tmp_path: Path) -> None:
    """Verifica se o JsonVillagerRepository lê corretamente os registros."""
    json_file = tmp_path / "villagers.json"
    data = [
        {
            "Name": "Tom",
            "Species": "Cat",
            "Personality": "Lazy",
            "Hobby": "Education",
            "Birthday": "1/1",
            "Color 1": "Red",
            "Color 2": "Blue",
            "Style 1": "Cool",
            "Style 2": "Simple",
            "Gender": "Male",
        },
        {
            "Name": "Bob",
            "Species": "Dog",
            "Personality": "Lazy",
            "Hobby": "Play",
            "Birthday": "1/2",
            "Color 1": "Yellow",
            "Style 1": "Cute",
        },
        {
            # Registro sem nome deve ser ignorado sem estourar erro
            "Species": "Frog"
        },
    ]
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    repo = JsonVillagerRepository(json_file)
    villagers = repo.load_all()

    assert len(villagers) == 2
    assert villagers[0].name == "Tom"
    assert villagers[0].species == "Cat"
    assert villagers[0].color_2 == "Blue"
    assert villagers[0].style_2 == "Simple"
    assert villagers[1].name == "Bob"
    assert villagers[1].color_2 == ""
    assert villagers[1].style_2 == ""


def test_json_player_profile_reader_reads_correctly(tmp_path: Path) -> None:
    """Verifica se o JsonPlayerProfileReader lê os perfis de jogadores."""
    json_file = tmp_path / "players.json"
    data = [
        {
            "ID do jogador": "julia",
            "Personality": "Peppy",
            "Species": "Squirrel",
            "Hobby": "Fitness",
            "colors": ["Pink", "White"],
            "styles": ["Cute", "Active"],
        },
        {
            "id": "gabriel",
            "personality": "Cranky",
            "color_1": "Black",
        },
        {
            # Registro sem identificador deve gerar resultado com erro
            "Personality": "Normal"
        },
    ]
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    reader = JsonPlayerProfileReader(json_file)
    results = list(reader.read())

    assert len(results) == 3

    # Primeiro resultado
    assert results[0].error is None
    assert results[0].profile is not None
    assert results[0].profile.player_id == "julia"
    assert results[0].profile.colors == ("Pink", "White")
    assert results[0].profile.styles == ("Cute", "Active")

    # Segundo resultado
    assert results[1].error is None
    assert results[1].profile is not None
    assert results[1].profile.player_id == "gabriel"
    assert results[1].profile.colors == ("Black",)
    assert results[1].profile.styles == ()

    # Terceiro resultado (erro)
    assert results[2].error is not None
    assert results[2].profile is None


def test_json_recommendation_writer_writes_correctly(tmp_path: Path) -> None:
    """Verifica se o JsonRecommendationWriter exporta o lote em JSON."""
    json_file = tmp_path / "output.json"

    villager1 = Villager(
        name="Tom",
        species="Cat",
        personality="Lazy",
        hobby="Education",
        birthday="1/1",
        color_1="Red",
        style_1="Cool",
    )
    rec = Recommendation(
        villager=villager1, score=0.85, explanation=["Cor", "Estilo"]
    )

    player_result = PlayerResult(
        source_line=1, player_id="julia", recommendations=[rec]
    )
    error_result = PlayerResult(source_line=2, error="Invalid row")

    batch_result = BatchResult(results=[player_result, error_result])

    writer = JsonRecommendationWriter(json_file, max_factors=2)
    writer.write(batch_result)

    assert json_file.exists()
    with json_file.open(encoding="utf-8") as f:
        written_data = json.load(f)

    assert len(written_data) == 1
    assert written_data[0]["jogador"] == "julia"
    recs = written_data[0]["recomendacoes"]
    assert len(recs) == 1
    assert recs[0]["posicao"] == 1
    assert recs[0]["villager"] == "Tom"
    assert recs[0]["compatibilidade"] == "85.0%"
    assert recs[0]["fatores"] == ["Cor", "Estilo"]
