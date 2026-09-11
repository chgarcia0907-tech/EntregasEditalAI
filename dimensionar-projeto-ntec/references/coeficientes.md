# Coeficientes e escalas

Fonte: Régua de Dimensionamento v0.1 do NTec. Valores marcados 🟡 são chute inicial ancorado na base histórica e ainda não calibrados — use e carimbe a versão, não trate como verdade.

## Índice

1. Premissas fixas
2. Escala de complexidade
3. Destino de RN e RNF
4. Multiplicador de contexto
5. Fatores de buffer
6. Blocos fixos
7. Travas de sanidade

---

## 1. Premissas fixas

| Premissa | Valor |
|---|---|
| Sprint | 15 dias, sempre |
| Equipe padrão | 1 AS/PM + 2 devs |
| Dedicação efetiva | 3h/dia (faixa declarada 2–4h) |
| 1 PD | 1 dia-dev útil a 3h |
| Velocidade base | 14 PD/sprint 🟡 |

Capacidade nominal seria 2 devs × 10 dias úteis = 20 PD. Os 14 reservam 30% para code review, integração front-back, correção da sprint anterior e as cerimônias. Ninguém entrega capacidade nominal.

**A velocidade base não é ajustada aqui.** Registre `velocidade_base_pd_sprint: 14` e a composição real da equipe em `meta.equipe`; quem aplica o ajuste é a skill 2, que faz toda a aritmética. Aplicar dos dois lados duplicaria o ajuste em silêncio.

A tabela de ajuste está abaixo só para você entender o que a composição significa — não a aplique:

| Situação | Efeito na velocidade |
|---|---|
| 1 dev | 7 PD/sprint |
| 2 devs (padrão) | 14 PD/sprint |
| Cada dev adicional | +7 (não +10 — overhead de comunicação) |
| Ao menos 1 veterano de 2+ projetos | ×1,15 |
| Equipe 100% de primeiro projeto | ×0,75 |

**ITIP, preço por sprint e conversão para reais não aparecem neste arquivo de propósito.** Pertencem à skill 2.

---

## 2. Escala de complexidade

| Complexidade | PD | Referência concreta |
|---|---|---|
| XS | 1 | Ajuste de UI, tela estática, CRUD trivial sem regra |
| S | 2 | CRUD com validação simples, listagem com filtro |
| M | 5 | Fluxo com regra de negócio, tela composta com endpoints, upload |
| L | 8 | Fluxo crítico multi-regra, dashboard com agregação, permissionamento |
| XL | 13 | Motor de cálculo, integração bidirecional documentada, geração de documento formatado |
| XXL | 21 | **Quebra obrigatória.** Se não quebra, é spike com decisão de seguir ou não |

Classifique por semelhança com a referência, não por previsão de tempo. "Isso se parece mais com um CRUD com validação ou com um motor de cálculo?" é uma pergunta em que pessoas concordam; "quantos dias isso leva?" não é.

**Confirmação humana:** toda feature em L, XL ou XXL sai com `confirmado_por: null`. É onde o erro custa caro em valor absoluto — errar uma XS em 100% custa 1 PD, errar uma XL em 30% custa 4.

**Escalonamento por regra de negócio:** se uma RF acumula 3 ou mais RN não triviais, ela sobe um degrau.

---

## 3. Destino de RN e RNF

Só **RF** pontua. É a única fonte de PD de desenvolvimento.

### RN — regra de negócio

Não vira linha pontuada. Vira regra **dentro** da RF que ela afeta, registrada na justificativa. Conte quantas RN não triviais cada RF acumula: a partir de 3, a feature sobe um degrau.

### RNF — requisito não funcional

| RNF | Destino |
|---|---|
| Segurança, autenticação, perfis de acesso | Bloco fixo de infra e auth |
| Performance sob volume, picos de uso | Multiplicador de volume |
| Disponibilidade, ambientes, regras de deploy | Bloco fixo de deploy |
| Offline, multi-dispositivo | Multiplicador |
| Usabilidade, identidade visual | Distribuído nas RF. Não vira sprint dedicada, salvo pedido explícito de design system |
| Auditoria, rastreabilidade, log | Append-only simples: embutido nas RF de escrita. Com encadeamento ou exigência de perícia: vira RF própria em L ou XL |

A linha de auditoria é a mais contraintuitiva e vale reler. "Toda alteração rastreada" costuma ser embutido; "trilha de auditoria com encadeamento verificável" é feature.

---

## 4. Multiplicador de contexto

Incide **apenas** sobre o subtotal de PD de desenvolvimento. Nunca sobre blocos fixos — senão discovery e deploy inflam junto com a complexidade técnica, e os efeitos deixam de ser separáveis na calibração.

Comece pelo formato e some os fatores presentes.

| Eixo | Opção | Valor 🟡 |
|---|---|---|
| Formato (base) | Web / WebApp-PWA / Mobile | 1,00 / 1,10 / 1,25 |
| Formato adicional simultâneo | cada um | +0,20 |
| Níveis de acesso | 1 / 2–6 com baixa diferença / 2–6 com grande diferença / 6+ | +0 / +0,05 / +0,15 / +0,25 |
| Multitenancy | não / dados separados / isolamento / instâncias isoladas | +0 / +0,10 / +0,20 / +0,50 e **trava** |
| Integração unidirecional documentada | cada uma | +0,05 |
| Integração bidirecional documentada | cada uma | +0,10 |
| Integração unidirecional sem doc | cada uma | +0,15 e cláusula em contrato |
| Integração bidirecional sem doc | cada uma | +0,25 e spike obrigatório |
| Integração sem API | — | Não pontua: spike de 1 sprint e decisão antes da proposta |
| Dependência de dados (bases soltas) | sim | +0,15 e acionar NDados |
| Offline | sim | +0,20 |
| Restrição de stack fora do monorepo | sim | +0,15 a +0,30 |
| Maturidade técnica alta (múltiplos times, regras de deploy) | sim | +0,15 |
| Maturidade "não tem" (cliente lento para decidir) | sim | +0,10 |
| Volume de uso alto ou com picos | sim | +0,10 |
| Terceiro no caminho crítico | sim | +0,10 e registro contratual |

**Registre dois números:** `multiplicador_bruto` (a soma real) e `multiplicador` (o bruto limitado a 2,0). Guardar só o truncado apagaria justamente o sinal que dispara o gate — um projeto que soma 2,4 não é dimensionável em escopo fechado, e isso precisa sobreviver no JSON.

**Teto 2,0.** Acima disso o projeto vai para escopo aberto ou é recusado, e a decisão sobe para o CP. Sinalize no resumo; não bloqueie sozinho.

**Trava:** multitenancy com instâncias isoladas é bloqueante por decisão explícita do CP. Registre em `contexto.travas`.

Alguns fatores carregam obrigação além do número — cláusula em contrato, spike obrigatório, acionar o NDados. Registre essas obrigações em `contexto.obrigacoes`, porque elas se perdem se ficarem só na tabela.

Liste os fatores marcados com o motivo, não só a soma. Quem revisa precisa poder discordar de um item específico sem refazer a conta inteira.

---

## 5. Fatores de buffer

Base **15%**. Some 5% por fator presente. Teto **40%**.

Como no multiplicador, registre `soma_bruta` e `total` (= bruta limitada a 0,40). Sem os dois, a verificação de que o total bate com os fatores falha sempre que houver mais de cinco fatores.

### Avaliáveis nesta skill

- [ ] Multiplicador de contexto acima de 1,3
- [ ] Duas ou mais integrações, ou qualquer integração sem documentação
- [ ] Terceiro no caminho crítico
- [ ] Equipe majoritariamente trainee, ou troca programada por edital ou desligamento
- [ ] Cliente com múltiplos times de aprovação ou autoridade de compra não identificada
- [ ] Setor regulado — saúde, financeiro, jurídico, educação regulada, incentivo fiscal

### Pendentes — vão para `buffer.fatores_pendentes`

Estes dois dependem de informação que esta skill não tem. Não chute nenhum dos dois; registre como pendente com o motivo, e a skill 2 resolve.

- **Projeto acima de 12 sprints** — depende do número de sprints, que só a skill 2 calcula. É a fronteira da troca semestral da Poli
- **Feature atípica sem benchmark, ou setor sem precedente** — depende da base dos últimos 8 projetos do núcleo. Se o usuário souber responder, pergunte; senão, deixe pendente

A definição de atípica é: sem precedente nos últimos 8 projetos **e** sem implementação de referência conhecida. Setor regulado, por ser uma lista fechada, você consegue avaliar sozinho — setor *sem precedente* você não.

Cada risco da matriz que aciona um fator deve declarar isso na coluna de efeito, e cada fator marcado precisa ter um risco correspondente. Risco cuja mitigação é "aplicar buffer", sem o buffer estar na conta, é mitigação inválida.

---

## 6. Blocos fixos

Em sprints. Cada bloco tem critério que vem de um campo já preenchido — não se escolhe, se lê.

| Bloco | Critério | Sprints 🟡 |
|---|---|---|
| Refino, discovery, setup, acessos | PRD + protótipo validado, cliente pequeno | 0,5 |
| ↳ | padrão | 1 |
| ↳ | 5+ fluxos críticos, ou maturidade técnica alta | 1,5 |
| ↳ | demanda pouco detalhada (conversa solta) | 2 |
| Infra, auth, níveis de acesso | 1 nível, sem multitenancy | 0,5 |
| ↳ | 2–6 níveis | 1 |
| ↳ | 6+ níveis ou multitenancy | 1,5 a 2 |
| Spikes | ver fórmula abaixo | soma |
| Teste com cliente | 10% do dev, piso 0,5 e teto 2 | — |
| Deploy | web / múltiplos ambientes do cliente | 0,5 / 1 |
| Publicação em lojas | só mobile; janela depende de terceiro | 1 a 3 |
| Garantia de 30 dias | não precifica, mas aloca 10% de 1 analista por 1 sprint no PCP | — |

**Fórmula de spikes:**

```
spikes = 0,5 × (features em "A avaliar")
       + 0,5 × (integrações sem documentação)
       + 1,0 × (integrações sem API)
```

A segunda parcela existe porque a tabela de multiplicadores exige spike para integração sem doc, e essa obrigação precisa ter um lugar na conta. Meia sprint para descobrir o contrato de uma API legada já é otimista — se você achar que é pouco no caso concreto, registre isso como risco em vez de inflar o número por conta própria.

**Fluxo crítico** tem definição fechada: a sequência que, se falhar, para a operação do cliente ou corrompe dado de dinheiro, de pessoa ou de obrigação legal.

**Criticidade 3** — projeto que para a operação ou tem prazo regulatório — proíbe combinar QA e UAT na mesma sprint. Registre em `blocos_fixos.qa_separado`.

---

## 7. Travas de sanidade

Só as que esta skill consegue avaliar. As travas de preço, de duração e de budget dependem de sprints e reais — pertencem à skill 2.

| Trava | Limite | Consequência |
|---|---|---|
| Multiplicador | `multiplicador_bruto` acima de 2,0 | Escopo aberto ou recusa. Decisão do CP |
| Multitenancy | instâncias isoladas | Bloqueante por decisão do CP |
| Escopo "A definir" | acima de 10% das linhas | Escopo fechado não se sustenta |
| Features em XXL | qualquer uma | Quebra obrigatória antes de fechar |

Estourar uma trava não impede o dimensionamento. A skill **sinaliza**, no resumo e em `contexto.travas`; a decisão de seguir pertence a uma pessoa.

**Sobre o delta.** Quando a validação acontece depois da venda — o caso comum no núcleo — não há o que cortar com o cliente sem renegociar. O delta entre vendido e dimensionado não se resolve aqui: ele é registrado para que alguém decida. Essa decisão pertence ao documento de validação, não a esta skill.
