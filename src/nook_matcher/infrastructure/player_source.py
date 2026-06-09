"""Leitura de perfis de jogadores a partir de CSV (padrão Repository).

Mapeia colunas por cabeçalho, ignora colunas desconhecidas e reporta
linhas inválidas sem abortar o lote (H2). Campos vazios viram "sem
preferência" no perfil resultante (H3).
"""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from nook_matcher.domain.entities import PlayerProfile, clean_text
from nook_matcher.infrastructure.headers import normalize_header


@dataclass(frozen=True)
class RowResult:
    """Resultado da leitura de uma linha do CSV de jogadores.

    Exatamente um entre ``profile`` e ``error`` é preenchido.

    Attributes:
        source_line (int): Número da linha no arquivo (1 é o cabeçalho).
        profile (PlayerProfile | None): Perfil válido lido da linha.
        error (str | None): Mensagem de erro, quando a linha é inválida.
    """

    source_line: int
    profile: PlayerProfile | None = None
    error: str | None = None


class PlayerProfileReader(ABC):
    """Contrato para iterar perfis de jogadores de uma fonte."""

    @abstractmethod
    def read(self) -> Iterator[RowResult]:
        """Itera os resultados de leitura, um por linha de dados.

        Returns:
            Iterator[RowResult]: Um resultado por linha (válido ou erro).
        """


class CsvPlayerProfileReader(PlayerProfileReader):
    """Lê perfis de jogadores de um arquivo CSV por cabeçalho."""

    def __init__(self, path: str | Path) -> None:
        """Inicializa o leitor com o caminho do CSV.

        Args:
            path (str | Path): Caminho do arquivo de jogadores.
        """
        self.path = Path(path)

    def _normalize_header(self, raw: str) -> str | None:
        """Mapeia um cabeçalho bruto para a chave canônica (PT/EN).

        Args:
            raw (str): Cabeçalho bruto vindo do CSV.

        Returns:
            str | None: Chave canônica, ou ``None`` se desconhecida.
        """
        return normalize_header(raw)

    def read(self) -> Iterator[RowResult]:
        with self.path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            header_map = {
                column: self._normalize_header(column)
                for column in (reader.fieldnames or [])
            }
            if "player_id" not in header_map.values():
                yield RowResult(
                    source_line=1,
                    error=(
                        "Cabeçalho sem coluna de identificador do " "jogador."
                    ),
                )
                return
            for line, row in enumerate(reader, start=2):
                yield self._build_row(line, row, header_map)

    @staticmethod
    def _build_row(
        line: int,
        row: dict[str, str],
        header_map: dict[str, str | None],
    ) -> RowResult:
        """Transforma uma linha de dados em ``RowResult``.

        Args:
            line (int): Número da linha no arquivo.
            row (dict[str, str]): Linha lida pelo ``DictReader``.
            header_map (dict[str, str | None]): Mapa coluna→chave canônica.

        Returns:
            RowResult: Perfil válido ou erro reportando a linha (H2).
        """
        data: dict[str, str] = {}
        for column, value in row.items():
            key = header_map.get(column)
            if key:
                data[key] = value
        player_id = clean_text(data.get("player_id"))
        if not player_id:
            return RowResult(
                source_line=line,
                error="Linha sem identificador do jogador.",
            )
        colors = tuple(
            color
            for color in (
                clean_text(data.get("color_1")),
                clean_text(data.get("color_2")),
            )
            if color
        )
        styles = tuple(
            style
            for style in (
                clean_text(data.get("style_1")),
                clean_text(data.get("style_2")),
            )
            if style
        )
        profile = PlayerProfile(
            player_id=player_id,
            personality=clean_text(data.get("personality")),
            species=clean_text(data.get("species")),
            hobby=clean_text(data.get("hobby")),
            colors=colors,
            styles=styles,
        )
        return RowResult(source_line=line, profile=profile)
