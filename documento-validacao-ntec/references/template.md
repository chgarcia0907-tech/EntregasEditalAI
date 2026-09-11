# Template do documento de validação

Sete seções, sempre nesta ordem. A padronização é o produto: validações com estruturas diferentes não se comparam, e validações incomparáveis não calibram a régua.

Origem de cada conteúdo:

- **`dim`** = o `dimensionamento.json` da skill 1
- **`val`** = o `validacao.json` que o `calcular.py` emitiu
- **você** = prosa que você escreve a partir dos dois

Números **sempre** vêm do `val`, nunca recalculados no texto.

---

## Cabeçalho

```markdown
# Documento de Validação — <projeto>

**Cliente:** <dim.meta.cliente>
**Responsável do cliente:** <dim.cliente.responsavel.nome> — <cargo>
**CN:** <dim.meta.cn> · **Validador:** <dim.meta.validador>
**Data:** <dim.meta.data>

**Prazo sinalizado ao cliente:** <dim.vendido.prazo_sinalizado_semanas> semanas
**Investimento:** R$ <dim.vendido.investimento_brl> (<parcelamento>)
**Modelo de escopo:** <dim.vendido.modelo_escopo>
**Equipe:** <devs> devs + <as> AS — <senioridade>

---
*Régua v<dim.meta.versao_regua> · velocidade <val.entradas.velocidade_ajustada> PD/sprint · ITIP <val.entradas.itip>*
```

A linha de carimbo no rodapé existe para que, quando a velocidade for recalibrada, seja possível saber qual documento saiu de qual régua. Sem ela, daqui a um semestre ninguém consegue comparar nada.

Quando `dim.vendido.houve_venda` for `false`, troque as três linhas comerciais por **"Dimensionamento anterior à proposta"**.

---

## 1. Parecer de consultoria

Vem inteiro de `dim.parecer`. Mantenha as subseções e o vocabulário — é a parte que o núcleo já faz bem.

```markdown
## 1. Parecer de consultoria

### 1.1 Pontos mal definidos ou ambíguos
### 1.2 Funcionalidades mais complexas do que parecem para o nível da equipe
### 1.3 Expectativas do cliente possivelmente fora da realidade
### 1.4 Decisões técnicas e de produto a questionar
### 1.5 Abordagens alternativas para reduzir risco
### 1.6 Adequação de stack e bibliotecas
### 1.7 O que NÃO usar nesse contexto
```

Duas regras de escrita:

- Item de 1.2 vem com a complexidade atribuída e **quem ainda precisa confirmar**
- Item de 1.4 vem com `pd_antes` e `pd_depois` quando existirem. Recomendação que economiza 8 PD e não mostra isso parece preferência de estilo; com o número, vira decisão

---

## 2. Dimensionamento

A memória de cálculo. Sem ela o número não é auditável.

```markdown
## 2. Dimensionamento

| ID | Feature | Módulo | Compl. | PD | Prioridade | Depende de | Confirmada por |
|----|---------|--------|--------|----|-----------|------------|----------------|

**PD de desenvolvimento:** <val.dimensionamento.pd_dev> em <features_contadas> features
**Multiplicador de contexto:** <val.entradas.multiplicador>
**PD ajustado:** <val.dimensionamento.pd_ajustado>
**Velocidade aplicada:** <val.entradas.velocidade_ajustada> PD/sprint
```

Liste só RF dentro do escopo. RN e RNF aparecem como nota sob a tabela, com o destino de cada um — bloco fixo ou multiplicador.

**Features sem confirmação entram em destaque**, não como rodapé:

> ⚠ As features F-02, F-05 e F-07 estão em L ou acima e ainda não foram confirmadas por um dev da stack. O número abaixo não é fechado até isso acontecer.

---

## 3. Matriz de riscos

```markdown
## 3. Matriz de riscos

| Risco | Probabilidade | Impacto | Mitigação | Efeito no buffer |
|-------|---------------|---------|-----------|------------------|

**Buffer aplicado:** <val.buffer.total> (base <base> + <n> fatores)
```

A coluna **Efeito no buffer** é o conserto do erro mais comum do formato antigo: identificar "prazo insuficiente" como risco alto, recomendar buffer em prosa, e apresentar o cronograma sem ele. A tabela vira plano de projeto; a ressalva embaixo dela não vira nada.

Se `val.buffer.fatores_pendentes` não estiver vazio, diga em voz alta:

> O buffer acima está subestimado: o fator "<fator>" não pôde ser avaliado porque <porque_pendente>.

---

## 4. Arquitetura e stack

De `dim.arquitetura` e `dim.parecer.stack`.

```markdown
## 4. Arquitetura e stack

### 4.1 Stack tecnológica
### 4.2 O que NÃO usar nesse contexto
### 4.3 Arquitetura lógica
### 4.4 Decisões técnicas que impactam prazo
```

A 4.2 é barata de escrever e impede equipe júnior de superengenheirar — mantenha mesmo quando parecer óbvio. A 4.4 lista as decisões que viraram `depende_de` e, portanto, moldaram o cronograma da seção 5.

---

## 5. Cronograma vendido

De `val.cronograma`, sem alteração.

```markdown
## 5. Cronograma vendido

| Sprint | Semanas | Objetivo | Features | PD | Entregáveis | Responsável |
|--------|---------|----------|----------|----|-----------  |-------------|

**Sprints dimensionadas:** <val.dimensionamento.sprints_total>
**Margem contratada:** <val.venda.margem_sprints> sprints
**Sprints vendidas:** <val.venda.sprints_vendidos> · **Semanas:** <val.venda.semanas_vendidas>
```

Você escreve **objetivo** e **entregáveis** de cada sprint; as features e o PD vêm do `val`.

Sprints de margem aparecem na tabela com objetivo *"Margem contratada — não alocar trabalho"* e sem features. Não as esconda: o cliente vê a data que está comprando e a equipe vê que margem é margem, não trabalho.

Se alguma sprint tiver `ociosidade` alta, é sinal de que uma feature grande empurrou o resto. Vale uma linha explicando, porque parece erro e não é.

---

## 6. Delta: vendido versus dimensionado

**A seção que justifica o documento.** Pule direto para a 7 apenas quando `houve_venda` for `false`.

```markdown
## 6. Delta: vendido versus dimensionado

|                  | Vendido | Dimensionado | Delta |
|------------------|---------|--------------|-------|
| Semanas          |         |              |       |
| Sprints          |         |              |       |
| Investimento     |         | —            | —     |
| ITIP implícito   |         |              |       |
```

A linha de **ITIP implícito** traduz atraso em dinheiro e costuma ser o argumento mais forte do documento. Um projeto bem precificado no cronograma otimista pode cair para o piso no prazo real: o preço não estava errado, ele só valia num prazo que não vai acontecer.

Com `delta_semanas` positivo, **exatamente uma** saída precisa estar marcada e preenchida:

```markdown
### Saída escolhida

- [ ] **Cortar escopo** — features: ___ · PD removido: ___ · aprovado por: ___
- [ ] **Negociar sprints adicionais** — quantas: ___ · com quem: ___ · status: ___
- [ ] **Consumir margem** — quanto: ___ · quanto sobra: ___
- [ ] **Aceitar o risco** — quem aceitou: ___ · o que acontece se estourar: ___
```

> **A validação não fecha com delta positivo e nenhuma caixa marcada.**
> Sem essa trava, a saída default é a quinta: a equipe absorve em silêncio e ninguém registra.

---

## 7. Pendências em aberto

De `dim.lacunas`, mais o que apareceu no caminho.

```markdown
## 7. Pendências em aberto

| Pendência | Quem resolve | Até quando | O que trava | Muda PD? |
|-----------|--------------|------------|-------------|----------|
```

`Muda PD = sim` separa pendência de bloqueio: essa tem spike alocado no cronograma e não se resolve "durante a imersão".

Feche com a assinatura — validador, e quem confirmou as features grandes. É registro, não formalidade: é o que permite voltar depois e saber quem olhou o quê.

---

## Antes de gerar o PDF

- [ ] Todo número do documento saiu do `validacao.json`, nenhum recalculado no texto
- [ ] Todos os avisos do script foram tratados ou explicitamente registrados
- [ ] As sete seções estão presentes e na ordem
- [ ] Features ≥ L sem confirmação aparecem em destaque, não em rodapé
- [ ] Com delta positivo, há exatamente uma saída marcada e preenchida
- [ ] O rodapé carimba versão da régua, velocidade e ITIP
