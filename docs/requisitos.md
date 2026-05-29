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

### História 1 — Prioridade Alta

Jogador de Animal Crossing quer ver os detalhes dos villagers que o sistema recomenda (aparência e traços de personalidade) para decidir se gostou antes de procurar o villager no jogo.

**Critérios de aceitação:**

- Cada recomendação de villager deve exibir nome, espécie, cor, tipo de personalidade, hobby e aniversário.
- A recomendação também deve mostrar quais características fornecidas pelo usuário influenciaram na recomendação.
- As recomendações são apresentadas em ordem decrescente de compatibilidade, com a porcentagem de compatibilidade visível ao lado de cada villager.

### História 2 — Prioridade Alta

Jogador de Animal Crossing quer inserir no sistema um arquivo com suas preferências e de outros amigos para receber em uma única execução as recomendações de villagers para cada um deles, sem fazer jogador por jogador.

**Critérios de aceitação:**

- O sistema aceita um arquivo com colunas mínimas: identificador do jogador, personalidade preferida, espécie preferida, hobby preferido e cor preferida.
- A saída associa cada jogador à sua lista de villagers recomendados.
- As colunas são identificadas pelo cabeçalho e não pela posição, seu houver colunas extras ou desconhecidas elas serão ignoradas sem causar falha.
- Se houver alguma linha com informações cruciais faltantes (sem identificador ou sem cabeçalho), o sistema reporta a linha com erro e segue processando os demais jogadores válidos.

### História 3 — Prioridade Média

Jogador de Animal Crossing quer que o sistema lide com preferências parciais nos dados de entrada, para não excluir jogadores que deixaram de preencher algum dos campos.

**Critérios de aceitação:**

- O programa trata os campos vazios como "sem preferência" e gera as recomendações apenas com base nos eixos preenchidos.
- Caso todos os campos estiverem vazios, retorna villagers aleatórios e sinaliza que nenhuma preferência foi utilizada.

### História 4 — Prioridade Baixa

Jogador quer que o sistema produza as mesmas recomendações ao processar o mesmo arquivo mais de uma vez, para garantir que os resultados sejam precisos e condizentes com suas preferências.

**Critérios de aceitação:**

- Com o mesmo arquivo de entrada e a mesma configuração, a saída é idêntica entre execuções consecutivas.
- Qualquer componente aleatório (desempate, amostragem) utiliza uma seed fixa registrada na configuração.

### História 5 — Prioridade Média

Jogador de Animal Crossing quer que cada villager recomendado venha acompanhado de uma justificativa ou quais preferências são compatíveis com o villager, para entender por que aquele villager específico foi indicado a ele.

**Critérios de aceitação:**

- Para cada villager recomendado, a saída exibe os principais fatores que contribuíram para a recomendação.
- O número de fatores exibidos é fixo e definido em configuração.
  
---

## 4. Registro de Validação

### Ambiguidades

- **A1 — "Aparência" (História 1) não está operacionalizada.** Inclui imagem do villager ou apenas descrição textual (espécie + cor)?
- **A2 — "Arquivo" (Histórias 2 e 4) sem formato definido.** CSV? Excel? JSON? _Revisão: CSV será utilizado_ 
- **A3 — "Principais fatores" (História 5) sem critério de corte.** Quantos fatores aparecem? Top 3, todos com peso acima de X, todos?

### Conflitos

- **C1 — História 1 (display detalhado) vs. História 2 (saída em arquivo batch).** A História 1 sugere uma exibição rica ("exibir nome, espécie, cor, personalidade, hobby, aniversário, fatores de match"). A História 2 diz que a saída é um arquivo associando jogador a recomendações. Como conciliar? O arquivo terá todas essas colunas? Haverá camada separada de visualização?
- **C2 — Histórias 1 e 5 restringem a escolha do modelo.** Gerar justificativas legíveis é trivial para modelos baseados em regras ou similaridade (KNN, cosseno), mas custoso para modelos black-box (redes profundas). _Revisão: KNN será utilizado_ 
- **C3 — "Cor preferida" do jogador (História 2) vs. policromia dos villagers.** Casar uma cor única do jogador com villagers que têm várias cores depende da decisão tomada em A1.
- **C4 — Histórias 1 e 5 dizem quase a mesma coisa.** "Características fornecidas pelo usuário que influenciaram a recomendação" (H1) ≈ "fatores que contribuíram para a recomendação" (H5). Ou são funcionalidades sobrepostas (redundância), ou são diferentes mas a distinção não está clara.

### Questões em aberto

- **Q1 —** Qual é a fonte de dados dos villagers (nome, espécie, cor, personalidade, hobby, aniversário)? Nookipedia (API)? Dataset custom construído pela equipe? _Revisão: CSV de villagers da Nookpedia será utilizado._ 
- **Q2 —** Formato e estrutura exata dos arquivos de entrada e saída (quais colunas? cabeçalho obrigatório? separador?).
- **Q3 —** Quantas recomendações por jogador? Top 5, top 10, configurável?
- **Q4 —** Caso extremo: o que o sistema faz quando *todos* os campos de preferência de um jogador estão vazios (História 3)?
- **Q5 —** Identificador do jogador: que tipo (string livre, número, e-mail)? Tem que ser único no arquivo? Como tratar duplicatas?
- **Q6 —** Aniversário do villager é apenas dado descritivo de saída ou pode entrar como fator de match (ex.: villagers que fazem aniversário no mesmo mês do jogador)?
- **Q7 —** Como validar a qualidade do modelo? Existe base de ground truth (ex.: "esse jogador realmente gostou desse villager") ou só avaliação subjetiva?
