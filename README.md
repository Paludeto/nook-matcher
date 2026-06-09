# NookMatcher 🦝🍃


## ⋆ Descrição

Nosso sistema empregará um algoritmo de machine learning para prever a compatibilidade entre o usuário e um conjunto de villagers de *Animal Crossing: New Horizons*, com base nos dados coletados, recomendando os mais compatíveis com o seu perfil.

## ⋆ Problema principal

Falta de uma ferramenta personalizada de recomendação, catálogo de villagers muito grande. Muitos jogadores têm preferências bem definidas e gostariam de encontrar villagers que se encaixem em critérios específicos, como espécie, oito tipos de personalidade (lazy, jock, cranky, smug, normal, peppy, snooty, sisterly), hobbies e estética visual. 

Diante de tantas variáveis, encontrar villagers verdadeiramente compatíveis com o perfil do jogador acaba sendo uma tarefa demorada e baseada em tentativa e erro.

## ⋆ Público-Alvo

Jogadores de Animal Crossing: New Horizons.

## ⋆ Como usar

### Instalação

Requer **Python 3.10+**. Na raiz do projeto (de preferência em um ambiente virtual):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Isso registra o comando `nookmatcher`.

### Execução

```bash
nookmatcher --input data/jogadores_exemplo.csv
```

A saída detalhada aparece no terminal e, **por padrão**, um arquivo CSV é gerado em
`output/recomendacoes_<timestamp>.csv` associando cada jogador às suas recomendações.

### Opções

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--input` | *(obrigatório)* | CSV com os perfis dos jogadores. |
| `--villagers` | `data/villagers.csv` | CSV do catálogo de villagers. |
| `--top-n` | `10` | Quantidade de recomendações por jogador. |
| `--seed` | `42` | Seed para resultados determinísticos. |
| `--max-factors` | `3` | Quantos fatores de justificativa exibir por villager. |
| `--output` | *(auto)* | Caminho do CSV de saída. |
| `--output-dir` | `output` | Pasta do CSV quando `--output` não é informado. |

Exemplo com opções:

```bash
nookmatcher --input data/jogadores_exemplo.csv --top-n 5 --output resultado.csv
```

### Entendendo os parâmetros

- **`--top-n`** — quantos villagers cada jogador recebe. O sistema calcula a
  compatibilidade com todos os villagers, ordena do mais para o menos compatível e
  devolve só os `N` primeiros. O padrão é `10` (limite de villagers de uma ilha). Não
  altera o cálculo, apenas o tamanho da lista.

- **`--max-factors`** — quantos motivos aparecem na justificativa de cada villager.
  Cada recomendação explica *por que* casou com o jogador, listando os critérios que
  bateram (personalidade, cor, hobby...) do mais para o menos relevante. Esta opção
  corta essa lista: com `3`, mesmo que cinco critérios casem, só os três principais são
  exibidos. Não altera o ranking, apenas o nível de detalhe da explicação.

- **`--seed`** — torna os resultados reproduzíveis. A única parte aleatória do sistema
  é o sorteio de villagers para jogadores que **não informaram nenhuma preferência**.
  A *seed* é o número que controla esse sorteio: com a mesma seed, o mesmo arquivo gera
  sempre a mesma saída. Trocar a seed muda quem é sorteado (mas continua reproduzível).
  Para jogadores com preferências, a seed não faz diferença — o ranking deles já é
  determinístico.

### Formato do arquivo de entrada

Um único CSV com **uma linha por jogador**. As colunas são identificadas pelo
**cabeçalho** (aceita português e inglês, sem diferenciar acento ou maiúsculas) e
colunas desconhecidas são ignoradas. Campos vazios são tratados como "sem preferência".

Colunas reconhecidas: `ID do jogador` (obrigatória), `Personality`, `Species`,
`Hobby`, `Color 1`, `Color 2`, `Style 1`, `Style 2`.

```csv
ID do jogador,Personality,Species,Hobby,Color 1,Color 2,Style 1,Style 2
julia,Peppy,Squirrel,Fitness,Pink,White,Cute,Active
gabriel,Cranky,,Music,Black,,Cool,
```

Linhas sem identificador são reportadas como erro, sem interromper o processamento dos
demais jogadores.

### Saída em CSV

Uma linha por par jogador×villager, com as colunas: `jogador`, `posicao`, `villager`,
`compatibilidade`, `especie`, `personalidade`, `hobby`, `cor`, `aniversario`, `fatores`.

## ⋆ Equipe

| Nome | Função |
|------|--------|
| Gabriel Paludeto | Machine Learning (modelo, treinamento, dados) |
| Julia Romanetto dos Santos | Aplicação (interface, integração, estrutura geral) |
