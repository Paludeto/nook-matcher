"""Normalização de cabeçalhos de CSV (PT/EN, sem acento/caixa).

Mapeia os nomes de coluna dos arquivos de entrada para chaves canônicas,
de forma que as colunas sejam identificadas pelo cabeçalho e não pela
posição, aceitando português e inglês e ignorando colunas desconhecidas
(H2).
"""

from __future__ import annotations

import unicodedata

# Apelidos de cabeçalho (já normalizados) → chave canônica interna.
_HEADER_ALIASES: dict[str, str] = {
    "name": "name",
    "nome": "name",
    "id do jogador": "player_id",
    "id do player": "player_id",
    "id jogador": "player_id",
    "id": "player_id",
    "identificador": "player_id",
    "jogador": "player_id",
    "player": "player_id",
    "player id": "player_id",
    "species": "species",
    "especie": "species",
    "gender": "gender",
    "genero": "gender",
    "sexo": "gender",
    "personality": "personality",
    "personalidade": "personality",
    "hobby": "hobby",
    "birthday": "birthday",
    "aniversario": "birthday",
    "data de nascimento": "birthday",
    "color": "color_1",
    "cor": "color_1",
    "color 1": "color_1",
    "cor 1": "color_1",
    "color1": "color_1",
    "cor1": "color_1",
    "color 2": "color_2",
    "cor 2": "color_2",
    "color2": "color_2",
    "cor2": "color_2",
    "style": "style_1",
    "estilo": "style_1",
    "style 1": "style_1",
    "estilo 1": "style_1",
    "style1": "style_1",
    "estilo1": "style_1",
    "style 2": "style_2",
    "estilo 2": "style_2",
    "style2": "style_2",
    "estilo2": "style_2",
}


def _canonicalize(raw: str | None) -> str:
    """Normaliza um cabeçalho: minúsculas, sem acento, espaços simples.

    Args:
        raw (str | None): Cabeçalho bruto vindo do CSV.

    Returns:
        str: Texto normalizado para consulta nos apelidos.
    """
    text = unicodedata.normalize("NFKD", raw or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(text.lower().split())


def normalize_header(raw: str | None) -> str | None:
    """Mapeia um cabeçalho bruto para a sua chave canônica.

    Args:
        raw (str | None): Cabeçalho bruto vindo do CSV.

    Returns:
        str | None: Chave canônica correspondente, ou ``None`` se a
        coluna for desconhecida (e, portanto, deve ser ignorada).
    """
    return _HEADER_ALIASES.get(_canonicalize(raw))
