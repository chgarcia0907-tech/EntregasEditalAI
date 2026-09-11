---
name: dimensionar-projeto-ntec
description: Transforma material bruto de um projeto — transcrição de reunião com cliente, protótipo do Lovable, anotações do CN — em um dimensionamento auditável do Núcleo de Tecnologia e Inovação da Poli Júnior: parecer de consultoria, inventário de features pontuado em PD, multiplicador de contexto, matriz de riscos com efeito no buffer, e a lista do que ainda falta descobrir. Emite o dimensionamento.json que a skill documento-validacao-ntec consome para montar cronograma e PDF. Use sempre que alguém mandar transcrição de reunião, print ou link de protótipo, ou notas de call e pedir para dimensionar, validar, "montar a validação", "rodar o dimensionamento", "montar o parecer", "quantas sprints isso dá", "quanto tempo isso leva", "isso cabe no que a gente vendeu", ou pedir estimativa de esforço, prazo ou preço de projeto de software. Dispara mesmo sem as palavras exatas — basta material bruto de projeto mais pedido de estimativa — e vale tanto antes da venda quanto para redimensionar projeto já vendido. Nunca estima o que não tem lastro na fonte: campo sem evidência vira lacuna registrada, não chute plausível.
---

# Dimensionar projeto — NTec

## Por que esta skill existe

O núcleo dimensiona projetos hoje por prompt gigante, que muda conforme o anexo e o contexto. O problema dele não é qualidade — é **variância**. Duas validações do mesmo projeto saem diferentes, e validações que não se comparam entre si não calibram nada.

Esta skill existe para produzir dimensionamentos **comparáveis**. Ela não precisa ser mais inteligente que o prompt que substitui. Precisa ser repetível, rastreável até a fonte, e honesta sobre o que não sabe.

Há uma armadilha específica a evitar. Um prompt grande, diante de uma lacuna, preenche com o que é plausível — e plausível parece certo. É assim que um projeto entra em execução com features que ninguém mencionou e sem as que o cliente pediu. **A lacuna declarada vale mais que o campo preenchido por adivinhação**, porque ela vira a pauta da próxima call do CN.

## O que esta skill produz e o que ela não produz

Ela produz **entradas**: features classificadas e pontuadas, fatores de contexto marcados, riscos, parecer, lacunas.

Ela **não** calcula sprints, semanas, preço nem ITIP. Isso é derivado, e quem deriva é a skill `documento-validacao-ntec`. Se o número calculado viajasse no JSON, as duas skills poderiam discordar e não haveria como saber qual está certa.

Consequência prática: quando você precisar de um número de sprints para decidir alguma coisa, você não pode tê-lo. Onde isso acontece, a skill diz o que fazer — normalmente, deixar o item pendente para a skill 2 resolver.

## Os dois momentos em que isso é usado

O mesmo dimensionamento serve duas situações, e a diferença muda o que é mais importante no resultado:

**Antes da venda.** O bloco `vendido` fica todo `null`. O produto é a base da proposta. Não invente prazo nem preço para preencher — é justamente o que a proposta vai decidir depois.

**Depois da venda** — o caso mais comum no núcleo. Preço e prazo já foram ditos ao cliente. Aqui o produto é a medida honesta do que foi vendido, para que a equipe de projetos não descubra o buraco depois de já estar dentro dele. **Nunca ajuste o dimensionamento para caber no que foi vendido.** O delta entre os dois é informação, não erro — e é a coisa mais útil que este trabalho produz.

## Antes de começar

Leia `references/coeficientes.md` e `references/contrato.md` por inteiro agora. Os dois governam decisões que começam já na extração — o destino de RN e RNF, o vocabulário controlado dos campos — e descobrir isso no meio obriga a refazer trabalho.

`references/parecer.md` pode esperar até a fase 4. `references/exemplo.md` mostra um caso pequeno resolvido de ponta a ponta; vale ler antes da primeira vez que você usar esta skill, e depois só por consulta.

## Fluxo

### Fase 1 — Inventário de fontes

Antes de extrair, liste o que existe e o que cada fonte pode legitimamente responder. Fontes diferentes têm autoridade sobre coisas diferentes, e confundir isso é a origem mais comum de feature inventada.

| Fonte | Responde bem | Não responde |
|---|---|---|
| Transcrição de reunião | Dor do cliente, orçamento, autoridade, urgência, expectativas, restrições declaradas | Lista de features. Cliente descreve problema, não requisito |
| Protótipo (Lovable) | Telas, rotas, fluxos, perfis de acesso — mapeia quase direto para RF | Regra de negócio, volume, criticidade |
| Notas do CN | Decisões do NTec (stack escolhida, abordagem), e desempate entre fontes | Fato sobre o cliente. Nota sem lastro em outra fonte é hipótese, não evidência |
| Proposta comercial | O que foi vendido: prazo sinalizado, investimento, modelo de escopo | O que é possível entregar |

Se houver **várias reuniões em datas diferentes**, a mais recente vence em caso de divergência — isso é evolução do entendimento, não contradição. Registre a mudança na justificativa da feature afetada. Contradição que exige lacuna é entre fontes da mesma época, ou quando a mais recente não cobre o ponto.

Se **não houver protótipo nem descrição de telas**, diga isso ao usuário e espere um inventário de features muito mais fraco. Não compense inventando.

### Fase 2 — Extrair com fonte

Toda afirmação de fato carrega de onde veio. O formato de `fonte` importa, porque "transcrição" não permite conferir nada:

- Transcrição: `transcricao 2025-08-12 00:22:31`
- Protótipo: `prototipo tela "Agenda semanal"`
- Nota: `nota CN 2025-08-13`
- Proposta: `proposta v2 p.3`

Preencha nesta ordem, porque as primeiras informam as seguintes:

1. **Cabeçalho e o que foi vendido** — cliente, responsável, e o bloco `vendido` (tudo `null` se ainda não houve venda)
2. **Produto e problema** — o que é, que dor resolve, quanto essa dor custa hoje ao cliente, e como o cliente mede sucesso
3. **Perfis de usuário** — quem usa e o que cada um faz. Isso determina os níveis de acesso, então precisa bater com o protótipo
4. **Comercial** — budget com origem, autoridade com nome e cargo, urgência com data e o que acontece se atrasar
5. **Perfil do cliente** — porte, maturidade técnica, restrições de stack, regras de deploy, nível de detalhamento da demanda

Campo sem evidência recebe `null` e uma entrada em `lacunas` com a pergunta pronta que o CN deve fazer. Não escreva "provavelmente" nem "estimado em" em campo de fato.

**Sobre evidência parcial.** Vários fatores têm um qualificador que a fonte pode não cobrir — "maturidade não tem (cliente lento para decidir)" quando você sabe que não há TI interna mas nada diz sobre velocidade de decisão. A regra é: **não marque, e abra lacuna nomeando o fator**. Isso subestima de propósito, e é a escolha certa porque um fator marcado sem evidência é invisível depois, enquanto uma lacuna nomeada é resolvida numa pergunta.

### Fase 3 — Inventário de features

Comece pelo protótipo, se houver. Cada tela e cada rota é candidata a requisito funcional. Depois varra a transcrição procurando o que o protótipo não mostra — regras, validações, integrações, relatórios.

Toda linha do inventário entra na lista `features`, inclusive RN e RNF: elas existem ali para rastreabilidade, com `pd: 0`. O que elas não fazem é **pontuar**. A razão é concreta: se "autenticação segura" e "controle de acesso por perfil" virarem PD, você conta duas vezes o que já está no bloco fixo de infra, e essa dupla contagem não aparece em lugar nenhum — o total só sai errado.

O destino de cada RN e RNF está em `coeficientes.md`. Alguns casos são contraintuitivos: auditoria simples é embutida, auditoria com encadeamento é RF própria.

Duas regras de granularidade que economizam discussão:

- Uma RF que não cabe em uma frase é mais de uma RF
- Uma RF sem tela e sem endpoint provavelmente é RN disfarçada

Preencha também `modulo` (agrupa features e alimenta a arquitetura), `prioridade` em MoSCoW (é a ordem de corte quando o budget não fecha, e a ordem de alocação no cronograma) e `depende_de` (o que precisa existir antes).

### Fase 4 — Parecer de consultoria

Aqui entra julgamento técnico, e é a parte de maior valor. Seis subseções, cada uma com efeito numérico declarado. Leia `references/parecer.md` antes de escrever a primeira.

O ponto que mais escapa: **ressalva de stack que exige construir algo por cima vira RF própria**, não nota de rodapé. "RBAC granular não vem pronto nessa lib, precisa ser construído em cima" é trabalho de verdade. Quando fica só como observação, esse PD some do dimensionamento e reaparece como hora não paga do analista.

### Fase 5 — Pontuar

Cada RF recebe XS, S, M, L, XL ou XXL, conforme as referências em `coeficientes.md`.

A pergunta que você responde não é "quanto tempo isso leva" — isso é previsão, e pessoas divergem muito ao prever. É "isso se parece mais com um CRUD com validação ou com um motor de cálculo?" — classificação contra referência, onde a concordância é bem maior.

Três travas que protegem o resultado:

- **XXL é quebra obrigatória.** Se não dá para quebrar, não é feature: é spike com decisão de seguir ou não. Registre em `parecer.ambiguidades` com `muda_pd: true`
- **Complexidade L ou acima sai sempre com `confirmado_por: null`.** Você propõe, um dev da stack confirma. É onde o erro custa caro em valor absoluto: errar uma XS em 100% custa 1 PD, errar uma XL em 30% custa 4
- **Quando a fonte não declara as regras de negócio**, você não pode aplicar o escalonamento de "3+ RN sobe um degrau" — porque teria que inventar as RN. Pontue pelo que está descrito, registre na `justificativa` até quantas regras a nota vale, e abra lacuna

### Fase 6 — Contexto, riscos e buffer

Marque os fatores de multiplicador presentes e some. O multiplicador incide **só** sobre o PD de desenvolvimento — nunca sobre blocos fixos, senão discovery e deploy inflam junto com a complexidade técnica e os efeitos deixam de ser separáveis na calibração.

Monte a matriz de riscos com probabilidade, impacto, mitigação e **efeito no buffer**. Essa última coluna impede o erro mais comum do formato antigo: identificar "prazo insuficiente" como risco alto, recomendar buffer em prosa, e apresentar o cronograma sem ele. A tabela vira plano de projeto; a ressalva embaixo dela não vira nada.

Dois fatores de buffer **não podem ser avaliados aqui** — "projeto acima de 12 sprints" depende de um número que só a skill 2 produz, e "feature atípica sem benchmark" depende da base histórica do núcleo, que você não tem. Ambos vão para `buffer.fatores_pendentes`, e a skill 2 os resolve. Não chute nenhum dos dois.

Liste os fatores marcados com o motivo, não só a soma. Quem revisa precisa poder discordar de um item específico sem refazer a conta inteira.

### Fase 7 — Emitir

Duas saídas, sempre:

1. **`dimensionamento-<cliente-slug>-<AAAA-MM-DD>.json`** na pasta de trabalho. Nome com cliente e data porque dois projetos no mesmo dia sobrescreveriam um arquivo genérico. Valide que o arquivo é JSON parseável antes de entregar
2. **Resumo legível** — o CN precisa conseguir ler sem abrir JSON

Rode as verificações de integridade de `contrato.md` antes de emitir, e registre no resumo qualquer trava estourada.

## Quando parar e perguntar

Seguir em frente nestes casos produz um número que parece bom e não é:

- **As fontes se contradizem** em algo que muda PD, e não é evolução temporal. Registre as duas versões com suas fontes e pergunte qual vale
- **O cliente descreveu só dor, nenhuma solução.** Isso vai para o parecer, não vira feature. Se o material inteiro for assim, o projeto ainda não é dimensionável
- **Mais de 10% das features ficariam como "A definir".** Escopo fechado não se sustenta assim. Sinalize e pergunte se o modelo de escopo deveria mudar — não bloqueie sozinho, a decisão é do CP

## O que nunca fazer

Cada item corresponde a uma forma conhecida de o dimensionamento sair errado parecendo certo.

| Nunca | Porque |
|---|---|
| Inferir valor plausível para campo sem evidência | É o comportamento do prompt gigante. Use `null` e registre a lacuna |
| Estimar o que foi vendido | Prazo e preço vendidos são fato. Se não estão na fonte, ficam `null` |
| Ajustar o dimensionamento para caber no vendido | O delta é o produto principal deste trabalho |
| Marcar `confirmado_por` em feature L ou acima | Só um humano confirma. A skill propõe |
| Transformar dor do cliente em feature | Dor vai para o parecer. Feature precisa de tela, endpoint ou regra |
| Dar PD a RN ou RNF | Elas entram no inventário com `pd: 0` e viram regra, multiplicador ou bloco fixo |
| Escolher entre fontes contraditórias da mesma época | Registre as duas e abra lacuna |
| Marcar fator de contexto ou buffer com evidência parcial | Não marque e abra lacuna nomeando o fator |
| Calcular sprints, semanas, preço ou ITIP | Derivados. Pertencem à skill 2 |

## Arquivos de referência

- **`references/coeficientes.md`** — escala PD, destino de RN e RNF, multiplicadores, fatores de buffer, blocos fixos, travas. Leia por inteiro antes de começar
- **`references/contrato.md`** — schema do JSON, vocabulário controlado e verificações de integridade. Leia por inteiro antes de começar
- **`references/parecer.md`** — como escrever cada subseção do parecer, com exemplos reais. Leia antes da fase 4
- **`references/exemplo.md`** — um caso pequeno resolvido de ponta a ponta. Leia na primeira vez; depois, consulta
