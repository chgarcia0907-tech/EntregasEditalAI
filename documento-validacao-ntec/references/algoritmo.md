# O algoritmo, e por que ele é assim

Documentação das decisões de desenho do `calcular.py`. Você precisa disto quando alguém perguntar "por que o cronograma ficou assim?" — e alguém vai perguntar.

---

## A decisão de fundo: aritmética, não julgamento

O núcleo hoje dimensiona por prompt gigante. O problema dele não é qualidade: é que ele muda conforme o anexo e o contexto, então duas validações do mesmo projeto saem diferentes. Validações incomparáveis não calibram nada.

Se a alocação de sprints fosse feita por inferência do modelo, a skill herdaria exatamente esse defeito. Por isso o cronograma é código.

**Critério de aceitação:** mesma entrada, mesma saída, byte a byte — inclusive se a ordem das features no JSON mudar. Se isso quebrar, o desenho quebrou.

É o que explica várias escolhas que parecem paranoicas: o `id` como último critério de ordenação, a iteração sobre listas ordenadas ao gerar avisos, o `sort_keys=True` no dump. Cada uma tapa um lugar por onde a ordem da entrada vazaria para o resultado.

---

## Sequência do cálculo

```
1. validar                    ids únicos, dependências existentes, pd vs complexidade
2. multiplicador              limitado a 2,0; o bruto é preservado
3. pd_ajustado por feature    pd × multiplicador, feature a feature
4. velocidade                 base do JSON, ajustada pela composição da equipe
5. alocar desenvolvimento     topológica + MoSCoW + guloso
6. blocos fixos               empacotados em slots de 1 sprint
7. sprints_total              blocos antes + dev + blocos depois
8. buffer                     resolve os fatores pendentes
9. sprints vendidos           ceil(total × (1 + buffer))
10. cronograma e delta
```

O multiplicador é aplicado **feature a feature**, não ao total. Se fosse ao total, o cronograma seria montado com PD bruto e depois escalado — e as sprints exibiriam um PD que não corresponde à duração que elas representam.

---

## Ordenação

```
nível topológico → MoSCoW → PD decrescente → id
```

**Nível topológico** primeiro porque dependência é restrição dura: o que precisa existir antes vem antes.

**MoSCoW** depois porque, dentro do que é possível fazer agora, o que o cliente mais precisa vem primeiro. Isso importa quando o projeto atrasa: o que sobra no fim é o que menos dói perder.

**PD decrescente** porque empacotar grandes primeiro deixa menos espaço ocioso — é o comportamento clássico do *first fit decreasing*.

**Id** por último, e é o critério que faz o teste de determinismo passar. Sem ele, duas features empatadas nos três primeiros critérios ficariam na ordem em que apareceram no JSON.

---

## Alocação de desenvolvimento

Empacotamento guloso com uma restrição: uma feature nunca entra numa sprint anterior ou igual à de qualquer dependência sua.

```python
minimo = max(sprint_da_dependencia) + 1
i = minimo
enquanto não couber em sprints[i]:  i += 1
```

Três comportamentos que parecem bug e são intencionais:

**Feature maior que a capacidade ocupa a sprint sozinha e a estoura.** Uma XL de 13 PD ajustada para 16 não cabe em 14 PD/sprint. Ela fica sozinha, e o `pd` da sprint sai acima da capacidade. Escondê-lo — quebrando a feature automaticamente — seria fingir que cabe. Aparecer é o ponto: quer dizer que a feature deveria ter sido quebrada no dimensionamento.

**Sprints podem ficar com ociosidade.** Quando uma dependência empurra uma feature grande para a frente, sobra espaço atrás. O campo `ociosidade` mostra quanto. É informação real sobre o projeto, não desperdício a esconder.

**Dependência fora da contagem é ignorada, com aviso.** Se F-05 depende de F-99 que está fora do escopo, o cronograma não tem como respeitar isso. O script ignora e avisa — em vez de quebrar ou de silenciar.

---

## Blocos fixos e a sprint de 15 dias

Sprint é sempre 15 dias. Não existe sprint de 3 semanas.

Essa regra existe porque validações antigas tinham sprints de duração variável — e quando sprint deixa de ser unidade, `PD ÷ velocidade = sprints` perde o sentido, já que a capacidade de cada sprint muda sem aviso. Cronograma legado com sprint de 3 semanas se converte como **1,5 sprint**.

Blocos fracionários **dividem** sprint: discovery de 0,5 e infra de 0,5 ocupam a mesma. A fração descreve quanto da sprint o bloco consome, nunca uma sprint mais curta.

---

## Buffer: a circularidade aparente

O fator "projeto acima de 12 sprints" existe porque acima disso o projeto cruza a troca semestral da Poli, e rotatividade vira risco estrutural. Isso é sobre calendário real, então o correto é avaliar contra as **sprints vendidas**, não as dimensionadas.

Só que as vendidas dependem do buffer, e o buffer depende do fator. Parece circular.

Não é, e a razão é a monotonicidade: **o fator só soma.** Se o total já passa de 12 sprints sem ele, passa com ele também. Então basta avaliar com o fator desligado e ligá-lo se necessário — uma passada, resultado estável, sem iteração.

O outro fator pendente, "feature atípica sem benchmark", depende da base histórica dos últimos 8 projetos do núcleo. Nenhuma das duas skills tem esse dado, então ele fica pendente até um humano responder pela flag `--atipica`. **Buffer com fator pendente está subestimado, e o documento precisa dizer isso** — é melhor do que preencher com chute.

---

## Arredondamento

```
sprints_vendidos  = ceil(sprints_total × (1 + buffer))
margem_sprints    = sprints_vendidos − sprints_total
semanas_vendidas  = sprints_vendidos × 2
```

Arredonda para cima porque não se vende meia sprint. Isso desvia um pouco da fórmula da régua (`Semanas_vend = Sprints_total × 2 × (1 + buffer)`), sempre na direção conservadora — a favor da equipe, nunca contra.

A margem aparece como **sprints próprias no fim do cronograma**, sem trabalho alocado. A alternativa seria diluir o buffer em todas as sprints, e ela é pior: a margem some de vista e é consumida sem ninguém perceber. Assim o cliente vê a data que está comprando e a equipe vê que margem é margem.

---

## O que o algoritmo não resolve

Vale saber antes que alguém descubra na hora errada.

**Não distribui PD por macroetapa.** A alocação é gulosa por dependência e prioridade, não otimizada por módulo. Sprints podem misturar módulos, e o resultado é um cronograma eficiente que às vezes é estranho de contar para o cliente. Agrupar por módulo custaria sprints a mais.

**Não modela férias, provas nem semana de edital.** Todas as sprints têm a mesma capacidade. Num núcleo de estudantes isso é otimismo conhecido, e é parte do que o buffer cobre.

**Não sabe paralelismo real entre devs.** A capacidade é um número agregado da equipe. Duas features independentes de 8 PD numa sprint de 14 podem ou não caber de verdade dependendo de quem pega o quê.

**Não reordena para caber no prazo vendido.** De propósito. Ajustar o cronograma até bater com o que foi vendido é exatamente o comportamento que o documento existe para tornar visível.

**Não valida se a velocidade está certa.** Ela é premissa de entrada, ainda não calibrada — e é a junta mais frágil do sistema inteiro, porque é o único elo cujo erro contamina tudo de forma proporcional e indistinguível.
