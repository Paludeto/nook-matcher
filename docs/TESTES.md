# Testes de Similaridade — `test_similarity.py`

## Contexto

Este arquivo cobre a camada de domínio do NookMatcher, especificamente o módulo `nook_matcher.domain.similarity`. Esse módulo implementa o cálculo de compatibilidade entre o perfil de um jogador e os villagers de Animal Crossing, usando o padrão **Strategy** para trocar a métrica de similaridade sem alterar o recomendador.

Foram escolhidas duas funções para teste:

| Função | Tipo |
|---|---|
| `_axis_overlap(profile, villager, axis)` | Função pura privada |
| `WeightedOverlapSimilarity.score(profile, villager)` | Método público da estratégia padrão |

---

## Estratégia de Teste

A suíte adota **testes unitários** com **pytest**, sem dependências externas ou mocks. A escolha se justifica pelo fato de ambas as funções serem **puras** — não realizam I/O, não têm estado mutável e sempre produzem o mesmo resultado para a mesma entrada. Isso torna o isolamento trivial e os resultados completamente determinísticos.

Para cada função foram escritos pelo menos três casos, classificados em:

- **Sucesso** — entrada válida e típica, com resultado esperado positivo.
- **Falha** — entrada válida que deve produzir resultado nulo ou zero (sem correspondência).
- **Borda** — valores limítrofes ou comportamentos não óbvios: preferências vazias, correspondência parcial em eixos com múltiplos valores, insensibilidade a maiúsculas/minúsculas e pesos customizados.

Os valores numéricos são verificados com `pytest.approx` para evitar falsos negativos por erros de ponto flutuante.

---

## Função 1 — `_axis_overlap`

Calcula a fração das preferências do jogador que é atendida por um villager em um único eixo (ex.: personalidade, cor). O resultado está sempre em `[0.0, 1.0]`.

### Casos de teste

| Teste | Tipo | Entrada | Resultado esperado |
|---|---|---|---|
| `test_single_value_full_match_returns_one` | Sucesso | `personality="Peppy"` (jogador e villager iguais) | `1.0` |
| `test_single_value_no_match_returns_zero` | Falha | Jogador quer `"Peppy"`, villager tem `"Lazy"` | `0.0` |
| `test_empty_preference_returns_zero` | Borda | Jogador sem preferência no eixo (`""`) | `0.0` |
| `test_case_insensitive_match` | Borda | `"PEPPY"` (jogador) vs `"peppy"` (villager) | `1.0` |
| `test_partial_multi_value_overlap` | Borda | Jogador quer `["Red", "Blue"]`; villager tem `["Red", "Green"]` | `0.5` |

**Raciocínio dos casos de borda:**
- *Preferência vazia*: a função deve retornar `0.0` e não lançar erro, pois eixos não preenchidos não penalizam o jogador.
- *Case-insensitive*: os dados do CSV podem vir com capitalização inconsistente; a função normaliza tudo para minúsculas antes de comparar.
- *Sobreposição parcial*: em eixos multivalorados (cor, estilo), o score é proporcional — 1 de 2 valores em comum equivale a `0.5`.

---

## Função 2 — `WeightedOverlapSimilarity.score`

Agrega o `_axis_overlap` de todos os eixos preenchidos pelo jogador, ponderando cada eixo por um peso configurável e normalizando pelo total de pesos. O resultado final fica em `[0.0, 1.0]`.

Os pesos padrão são: `personality=1.5`, `species=1.0`, `hobby=1.0`, `color=1.5`, `style=1.0`.

### Casos de teste

| Teste | Tipo | Cenário | Resultado esperado |
|---|---|---|---|
| `test_single_axis_full_match_score_is_one` | Sucesso | Apenas `personality` preenchida, match total | `value == 1.0`, chave `"personality"` em `per_axis` |
| `test_filled_axis_no_match_value_is_zero` | Falha | `personality` preenchida, sem match | `value == 0.0`, `per_axis["personality"] == 0.0` |
| `test_empty_profile_returns_zero_scoreresult` | Borda | Nenhum eixo preenchido | `ScoreResult(0.0, {})` exato |
| `test_all_axes_full_match_score_is_one` | Borda | Todos os 5 eixos preenchidos e correspondidos | `value == 1.0` (normalização garante o teto) |
| `test_custom_weights_change_score` | Borda | `personality` match, `species` sem match; dois conjuntos de pesos | Pesos padrão → `1.5/2.5 = 0.6`; pesos iguais → `1.0/2.0 = 0.5` |

**Raciocínio dos casos de borda:**
- *Perfil vazio*: deve retornar `ScoreResult(0.0, {})` sem iterar sobre nenhum eixo, pois não há com o que normalizar.
- *Match total em todos os eixos*: verifica o invariante de que a normalização mantém o score em `1.0` independentemente de quantos eixos estão preenchidos.
- *Pesos customizados*: confirma que a classe respeita o parâmetro `weights` e não ignora a configuração em favor dos pesos padrão.

---

## Como executar

```bash
# Da raiz do projeto
pytest tests/domain/test_similarity.py -v
```

Saída esperada: **10 passed**.

---

## Lacunas não cobertas

| Área | Motivo da ausência |
|---|---|
| `CosineSimilarity.score` | Outra estratégia do mesmo módulo; lógica semelhante mas fórmula diferente |
| `KNNRecommender` | Integração entre recomendador e estratégia; exigiria fixture de catálogo completo |
| Infraestrutura (CSV, `normalize_header`) | Camada separada; testes de infra pertencem a `tests/infrastructure/` |
| CLI (`presentation/cli.py`) | Requer I/O de arquivos; melhor coberto com testes de integração ou mocks de `argparse` |
| Testes baseados em propriedades | Ferramentas como **Hypothesis** explorariam o espaço de entradas de forma exaustiva, mas não foram incluídas por escopo |
