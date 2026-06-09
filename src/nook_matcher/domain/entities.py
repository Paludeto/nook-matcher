"""Entidades de domínio e constantes de eixos do NookMatcher.

Esta camada é pura: define os dados e os eixos de compatibilidade, sem
realizar I/O e sem depender da Infraestrutura.
"""

from __future__ import annotations

from dataclasses import dataclass

# Eixos categóricos usados no cálculo de compatibilidade. A ordem também
# define o desempate determinístico das justificativas (H4/H5).
AXES: tuple[str, ...] = (
    "personality",
    "species",
    "hobby",
    "color",
    "style",
)

# Rótulos legíveis (pt-BR) exibidos nas justificativas (H1/H5).
AXIS_LABELS: dict[str, str] = {
    "personality": "Personalidade",
    "species": "Espécie",
    "hobby": "Hobby",
    "color": "Cor",
    "style": "Estilo",
}


def clean_text(value: str | None) -> str:
    """Remove espaços nas pontas, tratando ``None`` como vazio.

    Args:
        value (str | None): Texto bruto, possivelmente vindo do CSV.

    Returns:
        str: Texto sem espaços nas extremidades; ``""`` quando ``None``.
    """
    return (value or "").strip()


@dataclass(frozen=True)
class Villager:
    """Villager de Animal Crossing com os atributos relevantes.

    Attributes:
        name (str): Nome do villager.
        species (str): Espécie (ex.: ``"Cat"``).
        personality (str): Tipo de personalidade (ex.: ``"Peppy"``).
        hobby (str): Hobby (ex.: ``"Fitness"``).
        birthday (str): Aniversário no formato do dataset (ex.: ``"7/2"``).
        color_1 (str): Cor primária.
        color_2 (str): Cor secundária (pode ser vazia).
        style_1 (str): Estilo primário.
        style_2 (str): Estilo secundário (pode ser vazio).
        gender (str): Gênero; não entra no cálculo de compatibilidade.
    """

    name: str
    species: str
    personality: str
    hobby: str
    birthday: str
    color_1: str = ""
    color_2: str = ""
    style_1: str = ""
    style_2: str = ""
    gender: str = ""

    @property
    def color(self) -> str:
        """Representação legível das cores para exibição (H1).

        Returns:
            str: ``"Cor1 / Cor2"`` quando há duas cores, a cor única
            quando há só uma, ou ``"—"`` quando não há nenhuma.
        """
        cores = [c for c in (self.color_1, self.color_2) if c]
        return " / ".join(cores) if cores else "—"

    def axis_values(self, axis: str) -> frozenset[str]:
        """Retorna os valores não vazios do villager para um eixo.

        Args:
            axis (str): Nome do eixo (ver :data:`AXES`).

        Returns:
            frozenset[str]: Valores do villager naquele eixo; vazio se o
            eixo for desconhecido ou não tiver valores.
        """
        return _axis_values(axis, self)


@dataclass(frozen=True)
class PlayerProfile:
    """Perfil de preferências de um jogador; eixos podem estar vazios.

    Attributes:
        player_id (str): Identificador do jogador no arquivo de entrada.
        personality (str): Personalidade preferida (vazio = sem pref.).
        species (str): Espécie preferida (vazio = sem preferência).
        hobby (str): Hobby preferido (vazio = sem preferência).
        colors (tuple[str, ...]): Cores preferidas (0, 1 ou 2 valores).
        styles (tuple[str, ...]): Estilos preferidos (0, 1 ou 2 valores).
    """

    player_id: str
    personality: str = ""
    species: str = ""
    hobby: str = ""
    colors: tuple[str, ...] = ()
    styles: tuple[str, ...] = ()

    def axis_values(self, axis: str) -> frozenset[str]:
        """Retorna as preferências não vazias do jogador para um eixo.

        Args:
            axis (str): Nome do eixo (ver :data:`AXES`).

        Returns:
            frozenset[str]: Preferências naquele eixo; vazio quando o
            jogador não informou nada para ele.
        """
        return _axis_values(axis, self)

    def filled_axes(self) -> list[str]:
        """Lista os eixos para os quais o jogador informou preferência.

        Returns:
            list[str]: Eixos preenchidos, na ordem de :data:`AXES`.
        """
        return [a for a in AXES if self.axis_values(a)]

    def has_preferences(self) -> bool:
        """Indica se o jogador informou alguma preferência (H3).

        Returns:
            bool: ``True`` se ao menos um eixo está preenchido.
        """
        return bool(self.filled_axes())


def _axis_values(axis: str, obj: Villager | PlayerProfile) -> frozenset[str]:
    """Extrai os valores de um eixo de um villager ou perfil.

    Args:
        axis (str): Nome do eixo (ver :data:`AXES`).
        obj (Villager | PlayerProfile): Entidade de origem.

    Returns:
        frozenset[str]: Valores não vazios; vazio se o eixo é
        desconhecido.
    """
    if axis == "personality":
        raw = (getattr(obj, "personality", ""),)
    elif axis == "species":
        raw = (getattr(obj, "species", ""),)
    elif axis == "hobby":
        raw = (getattr(obj, "hobby", ""),)
    elif axis == "color":
        raw = _color_values(obj)
    elif axis == "style":
        raw = _style_values(obj)
    else:
        raw = ()
    return frozenset(v for v in (clean_text(x) for x in raw) if v)


def _color_values(obj: Villager | PlayerProfile) -> tuple[str, ...]:
    """Coleta as cores de um villager (color_1/2) ou perfil (colors)."""
    if isinstance(obj, PlayerProfile):
        return obj.colors
    return (obj.color_1, obj.color_2)


def _style_values(obj: Villager | PlayerProfile) -> tuple[str, ...]:
    """Coleta os estilos de um villager (style_1/2) ou perfil (styles)."""
    if isinstance(obj, PlayerProfile):
        return obj.styles
    return (obj.style_1, obj.style_2)
