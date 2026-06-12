# NookMatcher — Explicação do Código

> Documento de apoio: explica o código em linguagem direta. Para o *porquê* das
> decisões (justificativas, padrões de codificação e git), veja
> [`docs/arquitetura.md`](docs/arquitetura.md); para os requisitos e a validação,
> veja [`docs/requisitos.md`](docs/requisitos.md).

## O que o NookMatcher faz

É uma ferramenta de linha de comando que **recomenda villagers de Animal Crossing: New Horizons** para jogadores. O jogador informa suas preferências (personalidade, espécie, hobby, cores, estilos) em um CSV; a ferramenta compara cada jogador contra o catálogo de villagers, ranqueia os mais compatíveis, explica *por que* cada um foi recomendado, e exporta tudo para um CSV — processando vários jogadores em lote.

O código segue **arquitetura em camadas (Clean Architecture)**: `domain` (regras puras) ← `application` (orquestração) ← `infrastructure` (I/O) ← `presentation` (CLI). A dependência sempre aponta para o domínio, que não conhece ninguém de fora.

---

## As quatro camadas e suas classes

### 🟢 Domain (`domain/`) — regras de negócio puras, sem I/O

| Arquivo | Classes/funções | Papel |
|---|---|---|
| `entities.py` | `Villager`, `PlayerProfile`, `AXES`, `AXIS_LABELS`, `clean_text` | Dados imutáveis (`frozen dataclass`). Ambos expõem `axis_values(axis)` para devolver, de forma uniforme, os valores de um **eixo** (personalidade, espécie, hobby, cor, estilo). `PlayerProfile` ainda sabe quais eixos foram preenchidos (`filled_axes`, `has_preferences`). `AXES` fixa a ordem dos eixos, que também serve de desempate determinístico. |
| `similarity.py` | `SimilarityStrategy` (ABC), `WeightedOverlapSimilarity`, `CosineSimilarity`, `ScoreResult` | **Padrão Strategy**: cada classe é uma forma de medir compatibilidade. Devolvem um `ScoreResult` com a nota global **e** a contribuição por eixo (`per_axis`). A versão ponderada (padrão) dá peso maior a personalidade e cor; considera só os eixos preenchidos e normaliza para `[0, 1]` (H3). |
| `explanation.py` | `ExplanationBuilder` | Transforma o `per_axis` do `ScoreResult` em frases legíveis ("Personalidade: Peppy"), ordenadas por relevância. É o "*por quê*" da recomendação (H1/H5). |
| `recommender.py` | `KNNRecommender`, `Recommendation` | O coração. Pontua todos os villagers com a `strategy`, anexa a justificativa via `ExplanationBuilder`, ordena (desempate determinístico por nome) e devolve o top-N. Se o jogador não tem preferências, sorteia com seed fixa (H3/H4). |

### 🟡 Application (`application/batch_service.py`) — orquestração

- **`BatchRecommendationService`**: recebe um `KNNRecommender` já carregado e um `PlayerProfileReader`. Itera os jogadores lidos pela infra, chama o recomendador para cada um, e coleta os erros por linha **sem abortar o lote** (H2). Devolve `BatchResult` (lista de `PlayerResult`, com totais `total_players`/`total_errors`).

### 🔵 Infrastructure (`infrastructure/`) — I/O e formatos externos

| Arquivo | Classes | Papel |
|---|---|---|
| `repositories.py` | `VillagerRepository` (ABC), `CsvVillagerRepository`, `InMemoryVillagerRepository` | **Padrão Repository**: carrega o catálogo de villagers. CSV em produção, em-memória nos testes. |
| `player_source.py` | `PlayerProfileReader` (ABC), `CsvPlayerProfileReader`, `RowResult` | Lê perfis dos jogadores linha a linha; cada `RowResult` traz **ou** um `PlayerProfile` válido **ou** um erro com o número da linha (H2). |
| `headers.py` | `normalize_header()` | Função utilitária: mapeia cabeçalhos de coluna (PT/EN, sem acento/caixa) para chaves canônicas. Usada pelos dois leitores → colunas são identificadas pelo nome, não pela posição. |
| `output_writer.py` | `CsvRecommendationWriter` | Escreve o `BatchResult` em CSV, uma linha por par jogador×villager. |

### 🟣 Presentation (`presentation/cli.py`) — entrada do usuário

- **`main()`**: parseia argumentos, valida caminhos, **monta o grafo de dependências** (é o composition root) e imprime no terminal.

---

## Como tudo se conecta (o fluxo de uma execução)

`main()` no `cli.py` é o **Composition Root** — o único lugar que instancia as implementações concretas e "costura" as peças (injeção de dependência manual). É também onde se confirma que os padrões são usados de fato, e não só descritos:

```
CsvVillagerRepository.load_all() ─┐
                                  ├─► KNNRecommender(strategy, villagers, seed)
WeightedOverlapSimilarity() ──────┘            │
                                               ▼
CsvPlayerProfileReader ──► BatchRecommendationService.run(top_n)
                                               │
                                               ▼  (por jogador)
                          KNNRecommender.recommend(profile, top_n)
                               │            │
                               ▼            ▼
                    SimilarityStrategy   ExplanationBuilder
                       .score()            .build()
                               │
                               ▼
                          BatchResult ──► _print_batch_result()  (terminal)
                                      └──► CsvRecommendationWriter.write()  (arquivo)
```

Passo a passo:

1. **`cli.main()`** lê os argumentos e cria: o repositório de villagers, o leitor de jogadores, a estratégia de similaridade, o `KNNRecommender` (já carregando o catálogo via `load_all()`) e o `BatchRecommendationService`.
2. **`service.run(top_n)`** percorre cada `RowResult` do leitor. Linha inválida → vira um `PlayerResult` com erro (H2). Linha válida → chama o recomendador.
3. **`recommender.recommend(profile, top_n)`** usa a `SimilarityStrategy` para pontuar cada villager (gerando `ScoreResult`) e o `ExplanationBuilder` para justificar, devolvendo `Recommendation`s ordenadas. Sem preferências → sorteio com seed fixa (H3/H4).
4. O serviço agrega tudo em **`BatchResult`**.
5. **`cli`** imprime o resultado **e** o **`CsvRecommendationWriter`** exporta o CSV — as duas saídas vêm do mesmo `BatchResult` (resolução do conflito C1 da validação).

## Os princípios de design por trás

- **Inversão de dependência via ABCs**: `SimilarityStrategy`, `VillagerRepository` e `PlayerProfileReader` são interfaces. As camadas de cima dependem da abstração — dá para trocar CSV por API, ou a métrica ponderada pela do cosseno, sem tocar no resto.
- **Padrões clássicos**: *Strategy* (similaridade), *Repository* (acesso a dados), *Value Object/DTO* (as `frozen dataclass`: `Villager`, `PlayerProfile`, `ScoreResult`, `Recommendation`).
- **Determinismo (H4)**: empates resolvidos por nome e seed fixa garantem saída reprodutível.
- **Tolerância a falhas (H2)**: um jogador com linha inválida não derruba o lote inteiro.
