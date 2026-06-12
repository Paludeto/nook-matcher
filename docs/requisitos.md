# ENGENHARIA DE SOFTWARE

**Entrega de Requisitos — Sprint 1**

Alunos: **Gabriel Paludeto · Julia Romanetto dos Santos**

---

## 1. Pitch da Proposta

O jogo Animal Crossing New Horizons possui mais de 400 villagers, e jogadores gastam horas em wikis decidindo quem convidar para as suas ilhas, já que elas possuem um limite máximo de apenas 10 villagers. A comunidade de Animal Crossing é extremamente seletiva com os habitantes de suas ilhas, promovendo rankings de popularidade recorrentemente e postando sobre os seus personagens favoritos em fóruns. Em meio a estes rankings, villagers que poderiam ser compatíveis com os jogadores acabam sendo deixados de escanteio em favor dos que possuem mais apelo popular.

O sistema NookMatcher resolve estes problemas com um quiz curto sobre o perfil do jogador (estética, personalidade desejada, paleta da ilha, ritmo de jogo) e retorna 10 villagers ranqueados por compatibilidade. Cada villager é um vetor de atributos, e o algoritmo combina filtragem por conteúdo e filtragem colaborativa, ajustando pesos conforme o feedback do usuário. Cada match vem com a razão da recomendação, e os dez formam um tema de ilha coerente.

O sistema é extremamente relevante para jogadores do game que gostariam de ter villagers que reflitam às suas preferências em suas ilhas, sem que estes jogadores desperdicem muito tempo em wikis, catálogos ou fóruns.

### Fontes

- [Belltree Forums — Dream villager lineup](https://www.belltreeforums.com/threads/can-i-see-your-dream-villager-lineup.601709/)
- [Reddit — Favourite villager](https://www.reddit.com/r/AnimalCrossingNewHor/comments/1qst6uj/whos_your_favourite_villager/)
- [Reddit — Goth/alt snooty villagers](https://www.reddit.com/r/AnimalCrossingNewHor/comments/1staztr/gothalt_snooty_villagers/)
- [Reddit — Western-themed villagers](https://www.reddit.com/r/AnimalCrossingNewHor/comments/1sfol1k/help_me_choose_villagers_for_my_western_themed/)
- [Reddit — Favourite jock villagers](https://www.reddit.com/r/AnimalCrossingNewHor/comments/1l8w3db/favourite_jock_villagers/)
- [Reddit — Please recommend me some villagers](https://www.reddit.com/r/AnimalCrossingNewHor/comments/11t47v0/please_recommend_me_some_villagers_highlighted/)

---

## 2. Elicitação — Roteiro e Síntese

### Roteiro utilizado

- Análise de similares e de conteúdo de comunidade, sem entrevistas nem questionários.
- Seis threads de fóruns de Animal Crossing, agrupadas em três padrões de uso: enquetes de favoritos (incluindo segmentadas por personalidade, como jock), montagem de lineups por tema estético (goth/alt, western) e pedidos diretos de recomendação.

### Achados

- Jogadores escolhem villagers por critérios múltiplos e combináveis (personalidade, espécie, cor, tipo de casa, tema da ilha) e criam regras próprias, como limitar quantos villagers de cada personalidade, espécie, cor e afins.
- Tema e personalidade aparecem como eixos dominantes de filtragem.
- A recorrência de pedidos de recomendação indica que a decisão é difícil o bastante para ser terceirizada à comunidade, que é a lacuna que o NookMatcher endereça. Os três padrões mapeiam direto nos inputs do quiz.

---

## 3. Histórias de Usuário

As histórias seguem o formato **"Como _\<persona\>_, eu quero _\<tarefa\>_, para
_\<benefício\>_"**, escrito em primeira pessoa e mantendo a tarefa (o que o
jogador faz) separada do benefício (o porquê).

### História 1 — Prioridade Alta

> **Como** jogador de Animal Crossing, **eu quero** ver os detalhes de cada
> villager recomendado (aparência e traços de personalidade), **para** decidir
> se gostei dele antes de procurá-lo no jogo.

**Critérios de aceitação:**

- Cada recomendação exibe nome, espécie, cor, tipo de personalidade, hobby e aniversário do villager.
- Cada recomendação indica quais preferências informadas pelo jogador influenciaram o resultado.
- As recomendações aparecem em ordem decrescente de compatibilidade, com a porcentagem de compatibilidade visível ao lado de cada villager.
- Os atributos do villager são exibidos na grafia original do catálogo (ex.: "Peppy", não "peppy").
- Quando um atributo do villager está ausente no catálogo, o campo é exibido como vazio ("—") sem interromper a apresentação dos demais.

### História 2 — Prioridade Alta

> **Como** jogador de Animal Crossing, **eu quero** enviar um único arquivo com
> as minhas preferências e as de outros jogadores, **para** receber as
> recomendações de todos em uma só execução, sem repetir o processo jogador por
> jogador.

**Critérios de aceitação:**

- O sistema aceita um arquivo CSV com, no mínimo, as colunas: identificador do jogador, personalidade, espécie, hobby e cor preferidos.
- A saída associa cada jogador à sua lista de villagers recomendados.
- As colunas são identificadas pelo cabeçalho, não pela posição; colunas extras ou desconhecidas são ignoradas sem causar falha.
- Linhas com informações cruciais faltantes (sem identificador, ou arquivo sem cabeçalho) são reportadas com o número da linha, e o processamento dos demais jogadores válidos continua.
- A ordem dos jogadores na saída preserva a ordem de leitura do arquivo de entrada.

### História 3 — Prioridade Média

> **Como** jogador de Animal Crossing, **eu quero** que o sistema aceite
> preferências parciais nos dados de entrada, **para** que jogadores que não
> preencheram todos os campos não fiquem de fora das recomendações.

**Critérios de aceitação:**

- Campos vazios são tratados como "sem preferência" e as recomendações usam apenas os eixos preenchidos.
- A compatibilidade é normalizada para a faixa `[0, 1]` considerando só os eixos preenchidos, de modo que a ausência de preferência em um eixo não penaliza nem favorece nenhum villager.
- Quando todos os campos estão vazios, o sistema retorna villagers aleatórios e sinaliza explicitamente que nenhuma preferência foi utilizada.

### História 4 — Prioridade Baixa

> **Como** jogador de Animal Crossing, **eu quero** obter as mesmas
> recomendações sempre que processar o mesmo arquivo, **para** confiar que os
> resultados são estáveis e refletem de fato as minhas preferências.

**Critérios de aceitação:**

- Com o mesmo arquivo de entrada e a mesma configuração, a saída é idêntica entre execuções consecutivas.
- Qualquer componente aleatório (desempate, amostragem) usa uma seed fixa registrada na configuração.
- Empates de compatibilidade são resolvidos por um critério estável e documentado (ordem alfabética do nome do villager), garantindo a mesma ordenação entre execuções.

### História 5 — Prioridade Média

> **Como** jogador de Animal Crossing, **eu quero** que cada villager
> recomendado venha acompanhado da justificativa da recomendação, **para**
> entender por que aquele villager específico foi indicado a mim.

**Critérios de aceitação:**

- Para cada villager recomendado, a saída exibe os principais fatores que contribuíram para a recomendação.
- O número de fatores exibidos é fixo e definido em configuração.
- Cada fator nomeia o eixo e o(s) valor(es) que casaram (ex.: "Personalidade: Peppy").
- Os fatores aparecem em ordem decrescente de relevância (contribuição ao score), e a justificativa de uma seleção aleatória (H3) sinaliza explicitamente a ausência de preferências.

---

## 4. Registro de Validação

### 4.1 Critérios de classificação

Para registrar os achados de forma consistente, distinguimos dois tipos de
problema:

- **Ambiguidade** — um único requisito admite mais de uma interpretação válida;
  resolve-se escolhendo uma delas e registrando a decisão.
- **Conflito** — dois requisitos competem ou se contradizem; satisfazer um
  dificulta o outro, exigindo uma decisão de projeto que concilie ambos.

Nesta revisão, dois itens antes listados como conflito foram **reclassificados
como ambiguidade** (A4 e A5): ambos dizem respeito à interpretação de um único
requisito, não à competição entre dois requisitos distintos.

### 4.2 Ambiguidades

- **A1 — "Aparência" (H1) não está operacionalizada.** Inclui imagem do villager ou apenas descrição textual (espécie + cores + estilo)?
- **A2 — "Arquivo" (H2 e H4) sem formato definido.** CSV? Excel? JSON?
- **A3 — "Principais fatores" (H5) sem critério de corte.** Quantos fatores aparecem? Top 3, todos com peso acima de X, todos?
- **A4 — "Cor preferida" do jogador (H2) vs. policromia dos villagers.** _(reclassificado de C3)_ Um único requisito — como casar a(s) cor(es) preferida(s) do jogador com villagers que têm até duas cores. A interpretação depende de A1, mas é a leitura de um requisito só, não a colisão de dois.
- **A5 — H1 e H5 parecem descrever a mesma capacidade.** _(reclassificado de C4)_ "Características que influenciaram" (H1) ≈ "fatores que contribuíram" (H5). A dúvida é interpretativa: são a mesma funcionalidade ou duas distintas? Não há contradição entre os requisitos, logo é ambiguidade, não conflito.

### 4.3 Conflitos

- **C1 — H1 (exibição detalhada) vs. H2 (saída em arquivo batch).** A H1 pede uma exibição rica (nome, espécie, cor, personalidade, hobby, aniversário, fatores); a H2 pede um arquivo associando jogador a recomendações. Satisfazer um formato dificulta o outro: é preciso decidir se o arquivo carrega todas as colunas ou se há uma camada de visualização separada.
- **C2 — H1/H5 (justificativas legíveis) vs. poder preditivo do modelo.** Gerar justificativas é trivial em modelos por similaridade (KNN, cosseno), mas custoso em modelos black-box (redes profundas). É um conflito real entre dois atributos de qualidade: explicabilidade e poder preditivo.

### 4.4 Questões em aberto

Resolvidas na validação (ver **4.5**): fonte de dados (CSV da Nookipedia),
formato e colunas de entrada/saída (CSV documentado no README), número de
recomendações por jogador (`--top-n`, padrão 10) e o comportamento quando todos
os campos estão vazios (seleção aleatória sinalizada).

Permanecem em aberto:

- **Q1 —** Identificador do jogador: que tipo (string livre, número, e-mail)? Precisa ser único no arquivo? Como tratar duplicatas?
- **Q2 —** Aniversário do villager é apenas dado descritivo de saída ou pode entrar como fator de match (ex.: villagers que fazem aniversário no mesmo mês do jogador)?
- **Q3 —** Como validar a qualidade do modelo? Existe base de ground truth ("esse jogador realmente gostou desse villager") ou só avaliação subjetiva?

### 4.5 Mapa de ajustes

Cada achado da validação foi traduzido em uma decisão e em um ajuste concreto nos
requisitos:

| Achado | Decisão | Ajuste aplicado |
|--------|---------|-----------------|
| **A1** (aparência) | Apenas descrição textual (espécie, cores e estilo); sem imagem. | H1 lista atributos textuais; não há campo de imagem nos critérios. |
| **A2** (formato) | CSV. | H2 e H4 fixam CSV; README documenta colunas e separador. |
| **A3** (corte de fatores) | Quantidade fixa e configurável (`--max-factors`, padrão 3). | H5 ganha o critério "número de fatores definido em configuração". |
| **A4** (cor vs. policromia) | Jogador e villager têm até duas cores; o match é por sobreposição parcial dos valores. | Entrada aceita `Color 1`/`Color 2`; o eixo cor casa por interseção (ver H1/H3). |
| **A5** (H1 ≈ H5) | São a mesma capacidade vista de ângulos diferentes: H1 = **exibir** os atributos; H5 = **explicar**, em ordem de relevância, por que casou. | Ambas mantidas, com escopos explicitados nos critérios; sem duplicação de funcionalidade. |
| **C1** (exibição vs. batch) | Uma única execução produz duas saídas do mesmo resultado: terminal (rico) e CSV (uma linha por par jogador×villager). | H1 e H2 deixam de competir: critérios separam exibição (terminal) de exportação (arquivo). |
| **C2** (explicabilidade vs. modelo) | KNN com similaridade categórica — explicável por construção. | H5 referencia os fatores por eixo produzidos pela métrica ponderada; sem modelo black-box. |
