"""Repositórios de acesso a dados de villagers (padrão Repository).

Isolam a Aplicação dos detalhes de armazenamento. A fonte atual é um CSV
da Nookipedia, mas a abstração permite trocá-la por uma versão em
memória (testes) ou por uma API no futuro.
"""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path

from nook_matcher.domain.entities import Villager, clean_text
from nook_matcher.infrastructure.headers import normalize_header


class VillagerRepository(ABC):
    """Contrato para carregar o catálogo de villagers."""

    @abstractmethod
    def load_all(self) -> list[Villager]:
        """Carrega todos os villagers disponíveis.

        Returns:
            list[Villager]: Catálogo completo de villagers.
        """


class InMemoryVillagerRepository(VillagerRepository):
    """Repositório em memória, útil para testes e prototipação."""

    def __init__(self, villagers: list[Villager]) -> None:
        """Inicializa o repositório com uma lista fixa de villagers.

        Args:
            villagers (list[Villager]): Villagers a serem servidos.
        """
        self._villagers = list(villagers)

    def load_all(self) -> list[Villager]:
        return list(self._villagers)


class CsvVillagerRepository(VillagerRepository):
    """Lê o catálogo de villagers de um arquivo CSV por cabeçalho.

    As colunas são identificadas pelo cabeçalho (PT/EN, sem acento/caixa)
    e colunas extras são ignoradas sem causar falha.
    """

    def __init__(self, path: str | Path) -> None:
        """Inicializa o repositório com o caminho do CSV.

        Args:
            path (str | Path): Caminho do arquivo de villagers.
        """
        self.path = Path(path)
        self.header_map: dict[str, str] = {}

    def load_all(self) -> list[Villager]:
        villagers: list[Villager] = []
        with self.path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self.header_map = {
                column: normalize_header(column)
                for column in (reader.fieldnames or [])
            }
            for row in reader:
                villager = self._build_villager(row)
                if villager is not None:
                    villagers.append(villager)
        return villagers

    def _build_villager(self, row: dict[str, str]) -> Villager | None:
        """Constrói um villager a partir de uma linha do CSV.

        Args:
            row (dict[str, str]): Linha lida pelo ``DictReader``.

        Returns:
            Villager | None: O villager, ou ``None`` se a linha não tem
            nome (registro sem identidade é ignorado).
        """
        data: dict[str, str] = {}
        for column, value in row.items():
            key = self.header_map.get(column)
            if key:
                data[key] = value
        name = clean_text(data.get("name"))
        if not name:
            return None
        return Villager(
            name=name,
            species=clean_text(data.get("species")),
            personality=clean_text(data.get("personality")),
            hobby=clean_text(data.get("hobby")),
            birthday=clean_text(data.get("birthday")),
            color_1=clean_text(data.get("color_1")),
            color_2=clean_text(data.get("color_2")),
            style_1=clean_text(data.get("style_1")),
            style_2=clean_text(data.get("style_2")),
            gender=clean_text(data.get("gender")),
        )
