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


class JsonPlayerProfileReader(PlayerProfileReader):
    """Lê perfis de jogadores de um arquivo JSON."""

    def __init__(self, path: str | Path) -> None:
        """Inicializa o leitor com o caminho do JSON.

        Args:
            path (str | Path): Caminho do arquivo de jogadores.
        """
        self.path = Path(path)

    def read(self) -> Iterator[RowResult]:
        import json

        try:
            with self.path.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as e:
            yield RowResult(
                source_line=1,
                error=f"Falha ao ler ou parsear o JSON: {e}",
            )
            return

        if not isinstance(data, list):
            yield RowResult(
                source_line=1,
                error="O JSON de jogadores deve ser uma lista de objetos.",
            )
            return

        for line, row in enumerate(data, start=1):
            if not isinstance(row, dict):
                yield RowResult(
                    source_line=line,
                    error="O registro do jogador não é um objeto JSON válido.",
                )
                continue

            # Mapeia as chaves usando normalize_header
            norm_row = {}
            for k, v in row.items():
                norm_k = normalize_header(k)
                if norm_k:
                    norm_row[norm_k] = v

            player_id = norm_row.get("player_id")
            if player_id is not None:
                player_id = str(player_id).strip()

            if not player_id:
                yield RowResult(
                    source_line=line,
                    error="Registro sem identificador do jogador.",
                )
                continue

            # Extrai cores e estilos (suportando tanto color_1/color_2 quanto listas colors/cores)
            def extract_list_or_val(val: any) -> list[str]:
                if val is None:
                    return []
                if isinstance(val, list):
                    return [str(x).strip() for x in val if x]
                if isinstance(val, str):
                    s = val.strip()
                    return [s] if s else []
                return [str(val).strip()]

            colors_list = []
            for k in ["colors", "cores"]:
                if k in row:
                    colors_list.extend(extract_list_or_val(row[k]))
            if not colors_list:
                c1 = extract_list_or_val(norm_row.get("color_1"))
                c2 = extract_list_or_val(norm_row.get("color_2"))
                colors_list = c1 + c2
            colors = tuple(colors_list)

            styles_list = []
            for k in ["styles", "estilos"]:
                if k in row:
                    styles_list.extend(extract_list_or_val(row[k]))
            if not styles_list:
                s1 = extract_list_or_val(norm_row.get("style_1"))
                s2 = extract_list_or_val(norm_row.get("style_2"))
                styles_list = s1 + s2
            styles = tuple(styles_list)

            def clean_json_text(val: any) -> str:
                if val is None:
                    return ""
                return str(val).strip()

            profile = PlayerProfile(
                player_id=player_id,
                personality=clean_json_text(norm_row.get("personality")),
                species=clean_json_text(norm_row.get("species")),
                hobby=clean_json_text(norm_row.get("hobby")),
                colors=colors,
                styles=styles,
            )
            yield RowResult(source_line=line, profile=profile)
