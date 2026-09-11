# Como escrever o parecer de consultoria

O parecer é a camada de julgamento técnico do dimensionamento. É a parte que um validador experiente faz bem e um formulário não captura.

A regra que atravessa todas as subseções: **cada item do parecer declara seu efeito numérico.** Uma recomendação que economiza 8 PD e não diz isso é conselho; a mesma recomendação com o número é decisão. Essa diferença é o que separa um parecer que muda o projeto de um que fica bonito no PDF.

Os exemplos abaixo vêm de validações reais do núcleo.

---

## 1.1 Pontos mal definidos ou ambíguos

Por item: `{descricao, quem_resolve, trava, muda_pd}`

A distinção que importa, e que o formato antigo não fazia: nem toda ambiguidade custa cronograma. "Volume real de usuários de apontamento de horas" e "grau de rigor jurídico exigido na elegibilidade fiscal" aparecem lado a lado na mesma lista, mas custam coisas muito diferentes.

- `muda_pd: true` → a feature correspondente vai para viabilidade **"A avaliar"**, o que aciona **spike de 0,5 sprint**
- `muda_pd: false` → é pendência administrativa. Vai para a lista de pendências sem custo de cronograma

**Exemplo real:**

> *Grau de rigor jurídico exigido na elegibilidade fiscal (Lei do Bem/MOVER) — precisa validação com time fiscal/jurídico do cliente.*
> `quem_resolve`: time fiscal do cliente · `muda_pd`: **true** — o motor de elegibilidade não pode ser especificado sem isso

> *Volume real de usuários de apontamento de horas.*
> `quem_resolve`: responsável do cliente · `muda_pd`: **false** — afeta dimensionamento de infra, não de escopo

Escreva o que **trava** se não resolver, não só o que falta. "Falta definir X" é menos útil que "sem X, a feature F-07 não pode ser especificada".

---

## 1.2 Funcionalidades mais complexas do que parecem para o nível da equipe

Por item: `{feature_id, porque, complexidade, confirmado_por}`

Esta subseção existe porque a equipe é de estudantes, frequentemente no primeiro projeto. Uma feature que seria M para um time sênior pode ser L aqui, e reconhecer isso na validação é mais barato que descobrir na sprint 4.

Regras:

- Todo item listado aqui é no mínimo **L**
- Todo item aqui exige confirmação de um dev da stack — sai da skill sempre com `confirmado_por: null`
- Todo item aqui precisa existir como linha na tabela de features. Item no parecer sem feature correspondente é escopo que ninguém vai pontuar

**Exemplos reais** — repare que o que os torna complexos raramente é a tela:

> Motor de elegibilidade fiscal multi-programa (Lei do Bem, MOVER, FINEP, BNDES, EMBRAPII) — regras distintas por programa, e cada uma muda com entendimento jurídico

> Vínculo de documento comprobatório em nível de atividade, não só de projeto — a modelagem do relacionamento é o custo, não o upload

> RBAC granular para 4 perfis — permissão cruzando perfil, área, projeto e confidencialidade

> Notificação automática de ausência de apontamento — exige job agendado, que é infraestrutura que o time pode nunca ter montado

Escreva o **porquê** em uma frase. "É complexo" não ajuda ninguém a discordar; "a regra muda por programa e cada uma depende de entendimento jurídico" permite que um dev diga "então é XL, não L".

---

## 1.3 Expectativas do cliente possivelmente fora da realidade

Por item: `{expectativa, realidade, registrado_em}`

Regra: toda expectativa listada precisa aparecer em **"explicitamente fora do escopo"** ou em **pendências com ação e prazo**. Expectativa registrada só no parecer não protege ninguém — quando o cliente cobrar, o parecer não é contrato.

Quando a conversa comercial já alinhou a expectativa, registre isso também. É informação positiva e evita que alguém reabra a discussão.

**Exemplo real:**

> *Cliente já está alinhado que o MVP não cobre o escopo completo do documento original — isso foi bem conduzido na reunião.*
> `realidade`: ponto de atenção é reforçar por escrito que o prazo cobre apenas o MVP
> `registrado_em`: pendência nº 4

---

## 1.4 Decisões técnicas e de produto a questionar

Por item: `{decisao_original, recomendacao, feature_id, pd_antes, pd_depois, adotada}`

A subseção de maior valor do parecer inteiro, e a que mais perde força quando não mostra números. É aqui que o validador reduz escopo por julgamento técnico, em vez de cortar feature no braço.

**Sobre `pd_antes` e `pd_depois`:** são pontuação de uma alternativa que não foi implementada, e portanto não têm fonte. Preencha só quando as duas pontas forem classificáveis pela escala com a mesma confiança que qualquer outra feature. Quando a alternativa for vaga demais para classificar, deixe `null` e escreva o raciocínio na recomendação — vale mais uma recomendação sem número que um número inventado.

**Sobre `adotada`:** marque `true` se a recomendação foi incorporada ao dimensionamento. Recomendação não adotada fica registrada como opinião técnica, mas não muda PD nem dependências.

**Exemplo real, e o que faltava nele:**

> *Motor de regra fiscal genérico e configurável desde o início → recomenda-se hardcode por programa (Lei do Bem, MOVER), generalizando depois.*

A recomendação está certa. O que faltava: isso é provavelmente a diferença entre **XL (13 PD)** e **M (5 PD)**. Oito PD é mais de meia sprint de uma equipe padrão. Sem o número, a recomendação parece preferência de estilo; com ele, vira a decisão mais barata do projeto.

Quando a recomendação **adiciona** PD, registre igual. Separar uma feature que estava modelada como uma só costuma custar mais no curto prazo e evitar retrabalho depois:

> *Aprovação de horas, notificação de ausência e valoração pelo RH devem ser três funcionalidades distintas, não etapas de uma só.*
> `pd_antes`: 8 (uma feature L) · `pd_depois`: 12 (M + S + M) · Justificativa: modelar junto gera retrabalho quando o cliente pedir para separar

---

## 1.5 Abordagens alternativas para reduzir risco

Por item: `{abordagem, risco_reduzido, efeito_cronograma}`

Se a abordagem muda a ordem de entrega, ela muda `depende_de` nas features. O cronograma precisa refletir a alternativa escolhida, não a original — senão o parecer recomenda uma coisa e o plano executa outra.

**Exemplos reais:**

> *Modularizar entregas por perfil: Colaborador e Gestor de horas primeiro, Financeiro e Administrador depois.*
> `efeito_cronograma`: altera dependências — features de Financeiro passam a depender do módulo de Horas concluído

> *Elegibilidade fiscal simplificada no MVP (marcação manual mais observação), automatizando regras após validação com o cliente.*
> `efeito_cronograma`: reduz PD agora, cria item de fase 2

---

## 1.6 Adequação de stack e bibliotecas

Por tecnologia: `{tecnologia, adequacao, ressalva, gera_rf, fator_contexto_relacionado}`

`adequacao` ∈ {adequado, com_ressalva, inadequado}.

`fator_contexto_relacionado` é **referência cruzada, não acréscimo**: aponta pelo nome o fator do multiplicador que esta ressalva justifica. O valor numérico mora em `contexto.fatores` e em lugar nenhum mais. Repetir o número aqui somaria duas vezes sem que nenhuma verificação pegasse.

**A regra que mais escapa, e a mais cara:** ressalva que exige construir algo por cima da biblioteca vira **RF própria**, não nota de rodapé.

**Exemplo real do erro:**

> *BetterAuth cobre bem login e OAuth social. Limitação: RBAC granular (perfil × área × projeto × confidencialidade) não vem pronto — precisa ser construído por cima da lib.*

Isso está tecnicamente correto e ficou só como observação. Mas "construir RBAC granular de quatro dimensões por cima de uma lib de auth" é trabalho real, e não foi pontuado em lugar nenhum. É exatamente o tipo de PD que some na validação e reaparece como hora não contabilizada do analista.

Regra prática, e ela tem uma fronteira: **configurar o que a lib oferece** cai no bloco fixo de infra; **implementar o que ela não tem** gera RF. Se a ressalva contém "precisa ser construído", "não vem pronto", "tem que implementar por cima" ou equivalente, crie a feature e preencha `gera_rf` com o id dela.

**Exemplo de ressalva que NÃO gera RF, mas gera restrição de modelagem:**

> *MongoDB é adequado para cadastro de projeto, horas e documentos, dado o schema flexível. Ressalva: lançamentos financeiros devem ficar em coleção própria, não embutidos no documento do projeto, para não comprometer a performance dos dashboards com agregações pesadas.*
> `gera_rf`: vazio · Isso é decisão de arquitetura e entra em `arquitetura.decisoes_que_impactam_prazo`

---

## 1.7 O que NÃO usar nesse contexto

Não é subseção obrigatória do JSON, mas é barata de escrever e vale muito para equipe júnior — impede superengenharia antes que ela aconteça.

Por item: o que evitar, por quê, e o que usar no lugar.

**Exemplos reais:**

> Motor de regras fiscais genérico e configurável — abstração desnecessária para o nível da equipe. Use hardcode por programa
>
> Filas e mensageria para notificações — cron job simples resolve
>
> Microserviços — monólito é suficiente; separar serviços agora só adiciona complexidade

---

## Verificação final do parecer

Antes de emitir, confira estes cruzamentos. Cada um corresponde a uma forma conhecida de o parecer e o dimensionamento discordarem:

- Todo item de 1.2 tem feature correspondente na tabela, com complexidade ≥ L e `confirmado_por: null`
- Todo item de 1.1 com `muda_pd: true` tem `feature_id` apontando para feature em "A avaliar", e spike contabilizado
- Toda expectativa de 1.3 aparece em `fora_do_escopo` ou em `lacunas`
- Todo item de 1.4 tem `pd_antes` e `pd_depois` preenchidos **ou** ambos `null` com a razão na recomendação
- Toda ressalva de 1.6 que descreve construção adicional tem `gera_rf` apontando para uma feature real
- Toda alternativa de 1.5 com `adotada: true` está refletida em `depende_de` ou em `features`
- Nenhum número de multiplicador foi repetido em `parecer.stack` — lá só vai o nome do fator
