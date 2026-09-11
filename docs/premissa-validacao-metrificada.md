# A premissa

## O que a Régua e o Manual estabelecem para uma validação metrificada

> **O que este documento é:** o argumento de por que a arquitetura construída no Notion — a Régua de Dimensionamento e o Manual de adoção — constitui base para uma validação metrificada, e sob quais condições esse argumento se sustenta.
>
> **O que ele não é:** nem o instrumento (isso é a Régua), nem o plano de implantação (isso é o Manual). É a camada que explica por que as duas peças foram desenhadas desse jeito e não de outro.
>
> **Estado:** protótipo. Os coeficientes não estão calibrados, e o documento diz onde isso importa.

---

## 1. O que significa validar de forma metrificada

A palavra "metrificada" costuma ser usada como sinônimo de "tem número". Não é. Um número pode ser tão arbitrário quanto uma opinião — e é pior, porque parece objetivo e fica difícil de contestar.

Uma validação é metrificada quando tem três propriedades, e só quando tem as três:

**Determinismo.** Duas pessoas com a mesma informação chegam ao mesmo resultado. Se o resultado depende de quem validou, o instrumento não está medindo o projeto — está medindo o validador.

**Decomponibilidade.** Quando o resultado erra, o erro tem endereço. "Subdimensionamos o projeto" não é diagnóstico; "erramos 30% nas features com integração não documentada" é. Só o segundo tipo de erro pode ser corrigido.

**Falseabilidade.** Existe um dado futuro capaz de mostrar que o instrumento está errado, e esse dado está definido antes de ser coletado. Um sistema que explica qualquer resultado depois do fato não mede nada.

Essas três propriedades são o critério contra o qual tudo o que foi construído deve ser julgado. Elas também são o motivo pelo qual o instrumento não pode ser avaliado por "o número parece razoável?" — essa pergunta não distingue medição de intuição bem-vestida.

---

## 2. Onde a validação atual falha nas três

| Propriedade | Estado hoje | Evidência |
|---|---|---|
| Determinismo | Ausente | O Dimensionamento Tec coleta informação e devolve ao validador a tarefa inteira de julgar. Nada no documento converte campo preenchido em número. A Seção 7 oferece quatro etapas em faixas de "1 a 4 semanas" — sozinhas, 12 semanas de amplitude sem nenhum critério de escolha dentro da faixa. |
| Decomponibilidade | Ausente | O resultado é um número agregado de sprints. Quando o projeto estoura, não há como saber se o erro veio do escopo, da velocidade da equipe ou de um fator de contexto. A lição que sobra é sempre a mesma e sempre inútil. |
| Falseabilidade | Ausente | Não existe registro do que foi estimado em unidade comparável com o que foi entregue. A view Controle registra semanas vendidas e TE, mas não o conteúdo daquelas semanas. Sem isso, nenhuma estimativa pode ser declarada errada com precisão. |

O sintoma agregado está na própria base: **TE real média de 70,81% contra TE prevista de 107,23%**, com casos individuais em 213% e 177%, e apenas 3 de 10 projetos na faixa saudável. Mas note que esse número é sintoma, não diagnóstico — a Seção 6 deste documento trata do que ele depende para ser lido corretamente.

---

## 3. Como cada peça entrega uma das propriedades

A Régua não é uma lista de regras arbitrárias. Cada elemento existe para produzir uma das três propriedades acima. Esta é a leitura que importa:

### Peças que produzem determinismo

**PD como unidade física.** 1 PD = 1 dia-dev útil a 3h de dedicação efetiva — dentro da faixa de 2 a 4h que o próprio núcleo declara. A escolha de ancorar a unidade em algo verificável no mundo, e não em uma abstração, tem uma consequência específica: se a premissa de 3h estiver errada, o erro é aproximadamente uniforme e desaparece na calibração da velocidade. Uma unidade abstrata não tem essa propriedade — erra de forma imprevisível e não corrigível.

**Escala XS a XXL com referência concreta.** A pergunta que o validador responde deixa de ser "quanto tempo isso leva?" — que é uma previsão — e passa a ser "isso se parece mais com um CRUD com validação ou com um motor de cálculo?" — que é uma classificação. Classificar contra referência é uma tarefa em que pessoas concordam muito mais do que prever.

**Blocos fixos com critério herdado.** Discovery, infra, teste e deploy deixam de ser faixas e passam a ser determinados por campos já preenchidos em outra seção. O nível de detalhamento da demanda define o discovery; o número de níveis de acesso define a infra. O validador não escolhe — ele lê.

### Peças que produzem decomponibilidade

**A separação RF / RN / RNF.** Só requisito funcional pontua. Regra de negócio vira regra dentro da feature que ela afeta; requisito não funcional vira multiplicador ou bloco fixo. Esta é a regra estruturalmente mais importante da Régua, e não depende de nenhum coeficiente: ela impede que "autenticação segura" seja contada como feature quando já está no bloco fixo de infra e auth. Sem ela, o total infla ou defla conforme quem preencheu, e o erro é invisível porque está distribuído.

**O multiplicador incide só sobre PD de desenvolvimento.** Nunca sobre blocos fixos. Isso mantém os efeitos separáveis: complexidade técnica não infla discovery, e discovery mal dimensionado não contamina o coeficiente de complexidade. Quando um dos dois erra, dá para saber qual.

**O buffer como checklist somável em vez de um número fixo.** Cada 5% tem um fator nomeado. Quando o buffer se mostra insuficiente, é possível perguntar qual fator estava subestimado — o que é impossível com uma gordura de 1,2 aplicada a tudo.

### Peças que produzem falseabilidade

**Os quatro campos novos da view Controle** — PD estimado, PD entregue, velocidade real e erro de dimensionamento. São o que fecha o loop. Sem eles a Régua é uma hipótese que nunca encontra o dado capaz de refutá-la, e em dois semestres vira mais um documento que ninguém atualiza.

**Os gates com dono definido.** Impedem que o número saia antes de as condições serem satisfeitas — o que preserva a integridade do registro. Uma estimativa emitida com 30% das features em "A definir" não é um dado ruim: é um dado que não pode ser usado para calibrar nada, porque não se sabe o que ela estava medindo.

**O critério de sucesso declarado antes.** TE entre 85% e 105% em 80% dos projetos. O número existe para poder ser não atingido.

---

## 4. A cadeia causal e onde cada elo pode falhar

O instrumento é uma cadeia. Ser explícito sobre ela é o que permite localizar o erro em vez de atribuí-lo ao conjunto.

```
PD_dev        = soma dos PD das RF dentro do escopo
PD_ajustado   = PD_dev × multiplicador de contexto
Sprints_dev   = PD_ajustado ÷ velocidade de referência
Sprints_total = blocos fixos + spikes + Sprints_dev + teste + deploy
Semanas_vend  = Sprints_total × 2 × (1 + buffer)
Preço         = ITIP × consultores × Semanas_vend
```

| Elo | Erro que pode introduzir | Como se detecta | Como se corrige |
|---|---|---|---|
| PD_dev | Escopo mal decomposto, ou RNF contado como feature | PD entregue muito diferente do estimado, sem padrão por fator | Revisar a classificação RF/RN/RNF; quatro olhos nas features grandes |
| Multiplicador | Coeficiente errado para um fator específico | Projetos com aquele fator erram sistematicamente na mesma direção | Ajustar aquele coeficiente, não o conjunto |
| Velocidade | Denominador errado | Erro proporcional e uniforme em todos os projetos | Recalcular como mediana das velocidades reais |
| Blocos fixos | Etapa subdimensionada | Semanas reais gastas naquela etapa vs. previstas | Ajustar o critério daquele bloco |
| Buffer | Incerteza mal precificada | Consumo acima do limiar antes da metade do projeto | Rever quais fatores marcam +5% |

**A implicação prática:** a velocidade é a junta mais frágil da cadeia, porque é o único elo cujo erro contamina tudo de forma proporcional e indistinguível. É possível pontuar escopo com precisão e ainda assim errar o resultado inteiro se 14 PD por sprint estiver longe do real. É também o número mais barato de medir — o que o torna a primeira prioridade de calibração, não a última.

---

## 5. O que a estrutura torna mensurável e hoje não é

Esta é a diferença prática entre o antes e o depois, independente de os coeficientes estarem certos:

- **Divergência entre validadores**, expressa em PD e localizada em features específicas — em vez de uma diferença de opinião sobre o total que ninguém consegue discutir.
- **Velocidade real por composição de equipe** — quanto uma dupla de primeiro projeto entrega comparada a uma com um veterano. Hoje isso é folclore.
- **Erro atribuível a um fator** — se projetos com integração não documentada erram 30% para cima de forma consistente, o coeficiente sai de 0,15 e vai para 0,25, e isso entra sozinho no próximo dimensionamento.
- **Consumo de buffer ao longo do projeto**, com limiar por sprint — o que transforma "o projeto está atrasado" de descoberta tardia em sinal antecipado.
- **Se um escopo fechado deveria ter sido aberto** — o multiplicador registra a decisão e permite verificar depois se o teto estava no lugar certo.

Nenhum desses itens exige que a Régua esteja calibrada. Todos exigem apenas que ela seja usada de forma consistente. Essa é a razão pela qual a estrutura tem valor antes dos números.

---

## 6. As três condições da premissa

O argumento acima só se sustenta se três coisas forem verdadeiras. Nenhuma das três está resolvida hoje, e isso precisa estar dito em voz alta — um instrumento que esconde suas pré-condições não é mais confiável, é só menos honesto.

### Condição 1 — a definição da TE

O diagnóstico "o núcleo subdimensiona" vem do contraste entre TE prevista de 107,23% e TE real de 70,81%. Essa leitura depende inteiramente de qual é a fórmula da TE na planilha de controle, e essa fórmula não foi confirmada.

Se TE for percentual de escopo entregue sobre tempo decorrido, **a direção do diagnóstico inverte** — e os coeficientes da Régua foram ancorados no sinal errado. O instrumento passaria a errar com mais confiança, que é o pior desfecho possível.

Custo de resolver: uma pergunta a quem mantém o PCP. Não há como prosseguir de forma responsável antes disso.

### Condição 2 — a velocidade precisa ser medida, não suposta

14 PD por sprint é um chute ancorado em raciocínio plausível: 2 devs × 10 dias úteis = 20 PD nominais, menos 30% de overhead. Plausível não é medido.

E há uma leitura alternativa dos dados que a Régua não refuta: talvez não haja subdimensionamento nenhum. Talvez o núcleo entregue exatamente o que três estudantes de 2 a 4h/dia entregam, e o que esteja errado seja a promessa vendida, não a conta feita. Se for isso, o problema está no denominador — a vazão — e nenhuma régua de escopo o resolve.

As duas hipóteses são observacionalmente equivalentes na base atual. Medir a velocidade real é o que as separa.

### Condição 3 — a fronteira entre multiplicador e buffer precisa estar escrita

Pelo menos cinco fatores aparecem nos dois lugares: integrações, feature atípica, setor atípico, terceiro no caminho crítico e maturidade técnica do cliente. Isso pode ser deliberado — uma integração sem documentação é de fato *mais trabalho* e *mais incerta* ao mesmo tempo. Mas a regra que distingue os dois não está escrita em lugar nenhum.

A formulação que resolve: **o multiplicador mede mais trabalho; o buffer mede incerteza sobre o trabalho.** Com ela no papel, cada um dos cinco fatores pode ser reavaliado e a permanência nos dois lados vira decisão registrada. Sem ela, o primeiro validador que notar a sobreposição vai concluir que é dupla contagem e cortar por conta própria — e aí o determinismo, que é a propriedade central, se perde na primeira semana de uso.

Esta é a única das três condições que é problema de arquitetura e não de dado. Não se resolve calibrando.

---

## 7. O que ainda não é premissa

Limites conhecidos, para que ninguém os descubra depois como se fossem defeitos escondidos:

**Escopo aberto não é dimensionado.** A Régua o usa apenas como válvula de escape quando o multiplicador estoura o teto de 2,0. Mas o Roadmap de Escopo Aberto exige cronograma das primeiras seis sprints, e isso também precisa de pontuação. É um vão real.

**Desenvolvimento é um bloco único.** A Régua atribui sprints por etapa para discovery, infra, teste e deploy, mas o desenvolvimento inteiro vira um número agregado. Isso custa granularidade: o post-mortem só consegue medir erro no nível do projeto, quando deveria medir por macroetapa ou módulo.

**Há parâmetros demais para a amostra.** Dezesseis linhas de multiplicador, oito fatores de buffer, dois tetos e uma velocidade — contra dez projetos concluídos para calibrar. Qualquer ajuste vai "acertar" por sobreajuste. Duas defesas: reduzir o número de botões antes do back-test, e declarar o critério de acerto **antes** de olhar os dados.

**O back-test histórico é circular e contaminado.** Os dez projetos foram escopados pelo formulário antigo. Comparar vendido com entregue mede a ancoragem da estimativa original, não a qualidade da Régua. E calibrar na base histórica reproduz o viés da base: se o núcleo vendeu barato, a Régua aprende a vender barato. Por isso o back-test deve medir **uma coisa só — a velocidade real** — e não tentar calibrar a tabela inteira.

**A Régua não resolve rotatividade nem vazão.** Ela precifica o risco de rotatividade com um fator de buffer. Não o reduz.

---

## 8. O critério de falsificação

O que transforma isto em premissa e não em crença é existir uma condição declarada de abandono.

**A Régua deve ser descartada se**, rodada retroativamente contra projetos concluídos, ela não previr a duração real melhor do que a estimativa do validador que os dimensionou à mão.

Esse critério tem que ser fixado antes de os dados serem olhados, incluindo a faixa de erro aceitável. Caso contrário o back-test confirma o que se quiser que ele confirme — e o instrumento terá comprado seu próprio resultado.

---

## 9. Como as três páginas se encaixam

| Página | Função | Pergunta que responde |
|---|---|---|
| **Dimensionamento Tec** | O formulário preenchido por projeto | Que informação existe sobre este projeto? |
| **Régua de Dimensionamento** | O instrumento que converte informação em número | O que cada resposta vale em PD, sprints e reais? |
| **Manual de adoção** | O plano de implantação | Quem faz o quê, quanto custa e em que ordem adotar? |

O elo faltante é entre a primeira e a segunda: hoje o formulário não aponta para a Régua, e as mudanças que a Régua lista como necessárias no formulário não foram executadas. Enquanto isso não for feito, existem duas fontes de verdade e o validador usa a antiga — que é exatamente o cenário em que a estrutura descrita neste documento não produz nenhuma das três propriedades.

---

## Resumo em uma página

A arquitetura construída entrega determinismo, decomponibilidade e falseabilidade — e entrega as três por desenho, não por acaso. Isso vale independentemente de os coeficientes estarem certos, porque **estrutura e parâmetros são separáveis**: é possível estar errado em todos os números e a arquitetura sobreviver, trocando o valor sem trocar o desenho.

Três coisas precisam ser verdade para a premissa se sustentar: a fórmula da TE precisa ser confirmada, a velocidade precisa ser medida em vez de suposta, e a fronteira entre multiplicador e buffer precisa ser escrita. A primeira custa uma pergunta. A segunda custa um back-test focado. A terceira custa uma frase.

Nenhuma delas custa o que já foi construído.
