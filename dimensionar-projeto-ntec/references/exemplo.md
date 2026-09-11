# Exemplo resolvido

Um recorte pequeno, de ponta a ponta, para calibrar **granularidade e tom**. Duas pessoas seguindo as mesmas regras ainda escrevem com verbosidade muito diferente, e a skill existe para reduzir variância — então este arquivo importa tanto quanto as regras.

Caso fictício, construído para conter os erros mais comuns.

---

## O material bruto

**Transcrição, 12/08, Clínica Vitalis**

> [00:15:02] Márcia (Diretora Administrativa): "Tem que ter acesso diferente pra recepção, pra médico e pra mim. O médico não pode ver a parte financeira de jeito nenhum, isso é sensível."
>
> [00:22:31] Rodrigo (TI terceirizado): "O MedSys tem uma API, mas eu nunca vi documentação. Acho que o pessoal deles manda um PDF quando você pede. A gente ia precisar puxar e também gravar de volta, porque o prontuário continua lá."
>
> [00:38:55] Márcia: "Ah, e o pessoal reclama muito da fila de espera, isso incomoda bastante os pacientes."

**Protótipo:** telas Login · Dashboard · Agenda semanal · Cadastro de paciente · Lista de convênios · Relatório de repasse por convênio

**Nota do CN:** "Falei em usar Supabase pra auth. Não falamos de valor na reunião."

---

## As decisões, uma a uma

### A fila de espera não vira feature

A Márcia mencionou um incômodo, não um pedido. Dor sem solução pedida vai para o parecer e para `fora_do_escopo` — nunca para `features`.

```json
{ "item": "Gestão de fila de espera",
  "porque": "Mencionada como incômodo, sem pedido de funcionalidade. Precisa ser levantada na próxima call",
  "fonte": "transcricao 2025-08-12 00:38:55" }
```

Se isso virasse uma feature, o projeto entraria em execução com escopo que ninguém contratou.

### O acesso do médico é RNF, não feature

"O médico não pode ver a parte financeira" é restrição de acesso. Entra no inventário para rastreabilidade, com `pd: 0`, e seu custo vive no bloco fixo de infra e auth.

```json
{ "id": "F-09", "nome": "Bloqueio do perfil Médico ao módulo financeiro",
  "modulo": "Infra e acesso", "tipo": "RNF", "escopo": "Dentro",
  "complexidade": null, "pd": 0, "prioridade": "Must", "depende_de": [],
  "viabilidade": "Viavel", "regras_de_negocio": [],
  "justificativa": "RNF de segurança — custo no bloco fixo de infra, não como RF. Dado de saúde sob LGPD: bloqueio no banco, não esconder menu",
  "fonte": "transcricao 2025-08-12 00:15:02", "confirmado_por": null }
```

Pontuar isso como feature contaria duas vezes o que já está no bloco de auth. É o erro que mais infla dimensionamento sem deixar rastro.

### A integração é XL, e sai não confirmada

```json
{ "id": "F-07", "nome": "Integração bidirecional com MedSys (leitura e escrita de prontuário)",
  "modulo": "Integracao", "tipo": "RF", "escopo": "Dentro",
  "complexidade": "XL", "pd": 13, "prioridade": "Must", "depende_de": ["F-04"],
  "viabilidade": "A avaliar", "regras_de_negocio": [],
  "justificativa": "O custo não é o cliente HTTP: é descobrir o contrato sem documentação, conciliar identidade de paciente entre os dois sistemas e tratar escrita parcialmente falha sem divergir o prontuário. Nota vale para o escopo descrito; se houver conciliação de histórico, sobe",
  "fonte": "transcricao 2025-08-12 00:22:31", "confirmado_por": null }
```

Repare em quatro coisas:

- `complexidade: XL` e `confirmado_por: null` — a skill propõe, o dev confirma
- `viabilidade: "A avaliar"` — sem documentação não dá para especificar, e isso aciona spike
- A `justificativa` diz **por que** é caro, em termos que permitem um dev discordar com precisão
- A última frase declara **até onde a nota vale**. Isso é o que fazer quando a fonte não cobre tudo

A ambiguidade correspondente:

```json
{ "descricao": "Documentação da API do MedSys nunca foi vista; não se sabe se permite escrita",
  "quem_resolve": "Rodrigo (TI terceirizado) junto ao fornecedor MedSys",
  "trava": "Sem isso a F-07 não pode ser especificada, e ela é 30% do desenvolvimento",
  "muda_pd": true, "feature_id": "F-07" }
```

E a lacuna, escrita como pergunta pronta:

```json
{ "campo": "features.F-07.complexidade",
  "porque": "Sem documentação da API não se sabe se há escrita nem qual a autenticação",
  "pergunta_para_o_cliente": "Rodrigo, você consegue pedir hoje ao MedSys a documentação da API? Precisamos saber quais entidades ela expõe, se permite escrita e como autentica.",
  "muda_pd": true }
```

Compare com o que **não** escrever: `{"campo": "API", "porque": "falta info", "pergunta_para_o_cliente": "perguntar sobre a API"}`. Ninguém consegue usar isso numa call.

### O Supabase é decisão do NTec, não fato sobre o cliente

A nota do CN não tem lastro em outra fonte. Ela serve para registrar uma decisão nossa — não vira `cliente.restricao_stack`, que fica `null` com lacuna.

```json
{ "tecnologia": "Supabase Auth", "adequacao": "com_ressalva",
  "ressalva": "Cobre login e perfis básicos. Bloqueio do Médico ao financeiro precisa ser construído como política no banco, não apenas no front",
  "gera_rf": [], "fator_contexto_relacionado": null }
```

`gera_rf` está vazio porque a política de acesso cai no bloco fixo de infra. **Se a ressalva exigisse construir um módulo de permissão próprio**, aí geraria RF — é a diferença entre "configurar o que a lib oferece" e "implementar o que ela não tem".

### Fatores marcados, e os que ficaram de fora

```json
"fatores": [
  { "fator": "Niveis de acesso 2-6 com grande diferenca", "valor": 0.15,
    "porque": "Recepcao, Medico e Direcao com diferenca forte — Medico bloqueado no financeiro" },
  { "fator": "Integracao bidirecional sem documentacao", "valor": 0.25,
    "porque": "MedSys: leitura e escrita, documentacao nunca vista" },
  { "fator": "Terceiro no caminho critico", "valor": 0.10,
    "porque": "Fornecedor MedSys controla o acesso a API" }
]
```

Multiplicador bruto e final: 1,50 (abaixo do teto, então iguais).

**Não marcado, de propósito:** `maturidade_tech` "não tem" daria +0,10. A clínica não tem TI interna, mas nada na transcrição diz que decide devagar — que é o qualificador do fator. Evidência parcial não marca; abre lacuna:

```json
{ "campo": "contexto.fatores — maturidade tech",
  "porque": "Sabemos que nao ha TI interna, mas nao ha evidencia sobre velocidade de decisao",
  "pergunta_para_o_cliente": "Marcia, quando surge uma duvida tecnica, quem decide e em quanto tempo costuma sair a resposta?",
  "muda_pd": false }
```

Isso subestima de propósito. É a escolha certa porque um fator marcado sem evidência é invisível depois; uma lacuna nomeada morre numa pergunta.

### Buffer: o que dá para avaliar e o que não dá

```json
"buffer": {
  "base": 0.15,
  "fatores": [
    { "fator": "Multiplicador acima de 1,3", "valor": 0.05, "porque": "Esta em 1,50" },
    { "fator": "Integracao sem documentacao", "valor": 0.05, "porque": "MedSys" },
    { "fator": "Terceiro no caminho critico", "valor": 0.05, "porque": "Fornecedor MedSys" },
    { "fator": "Setor regulado", "valor": 0.05, "porque": "Saude — LGPD e dado sensivel" }
  ],
  "fatores_pendentes": [
    { "fator": "Projeto acima de 12 sprints",
      "porque_pendente": "Depende do total de sprints, que so a skill 2 calcula" },
    { "fator": "Equipe majoritariamente trainee",
      "porque_pendente": "Composicao da equipe ainda nao alocada" }
  ],
  "soma_bruta": 0.35, "total": 0.35
}
```

Cada fator marcado tem um risco apontando para ele:

```json
{ "risco": "Fornecedor MedSys nao entregar documentacao da API a tempo, ou a API nao permitir escrita",
  "probabilidade": "Alta", "impacto": "Alto",
  "mitigacao": "Spike na sprint 1 com go/no-go; plano B de leitura apenas no MVP",
  "fator_buffer": "Integracao sem documentacao" }
```

`fator_buffer` guarda o **nome**, não o número. É o que permite conferir que nada foi contado duas vezes.

---

## Como o resumo abre

> **Lacunas — perguntas para a próxima call.** As três primeiras mudam PD.
>
> 1. *"Rodrigo, você consegue pedir hoje ao MedSys a documentação da API?"* — precisamos saber quais entidades expõe, se permite escrita e como autentica. A F-07 (13 PD, 30% do desenvolvimento) inteira depende disso.
> 2. *"Quando um convênio paga, onde esse pagamento é registrado hoje?"* — manual, extrato ou arquivo de retorno? A diferença é entre M e L.
> 3. *"O histórico da planilha entra no sistema ou começa do zero?"* — migração nunca foi mencionada. Se precisar, é feature não dimensionada.

Note o que o resumo **não** faz: não abre com "43 PD". O número vem depois das lacunas e das confirmações pendentes, porque só vale quando alguém confirmar as features grandes. Abrir pelo número convida a tratá-lo como pronto — e ele não está.
