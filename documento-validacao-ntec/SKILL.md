---
name: documento-validacao-ntec
description: Gera o documento de validação padronizado do Núcleo de Tecnologia e Inovação da Poli Júnior a partir de um dimensionamento.json produzido pela skill dimensionar-projeto-ntec — cronograma vendido sprint a sprint, conversão para semanas e preço, e a seção de delta entre o que foi vendido e o que foi dimensionado. O cronograma é calculado por script determinístico, nunca inferido: duas execuções com a mesma entrada produzem o mesmo cronograma. Use sempre que houver um dimensionamento.json e alguém pedir para "gerar a validação", "montar o documento", "fazer o cronograma", "fechar a validação", "gerar o PDF da validação", "quantas sprints ficou", "qual o preço", "cabe no que foi vendido", ou pedir o cronograma de sprints de um projeto já dimensionado. Dispara também quando o usuário manda o dimensionamento.json sem pedir nada específico, e quando quer recalcular a validação com outra velocidade, outro ITIP ou outra composição de equipe. Se não existir dimensionamento.json ainda, use antes a skill dimensionar-projeto-ntec.
---

# Documento de validação — NTec

## Por que esta skill existe

O núcleo produz validações que não se comparam entre si. Cada uma sai com estrutura própria, sprints de duração variável e o número derivado de um jeito diferente — e validações incomparáveis não calibram nada, o que trava a régua inteira no chute.

Esta skill produz **um documento só, sempre igual, com a mesma lógica de estimativa de tempo e preço**. É o que o núcleo não consegue fazer hoje.

## O princípio inegociável

**Cronograma é aritmética, não julgamento.**

Se o modelo alocar features em sprints por inferência, duas rodadas com a mesma entrada dão cronogramas diferentes — e aí o problema que a skill deveria resolver continua de pé, só que com outra roupa.

Por isso o cálculo inteiro mora em `scripts/calcular.py`. Seu trabalho nesta skill é: rodar o script, ler o resultado, e **escrever a prosa** do documento. Você não recalcula sprints, não ajusta o buffer no olho, não arredonda preço. Se um número parecer errado, o conserto é na entrada ou no script — nunca no texto.

O teste que prova isso: rodar duas vezes o mesmo arquivo produz `validacao.json` byte a byte idêntico, inclusive se a ordem das features na entrada mudar.

## Fluxo

### 1. Rodar o cálculo

```bash
python scripts/calcular.py dimensionamento-<cliente>-<data>.json --itip 1200
```

Flags:

- `--itip` — ITIP por consultor-semana. Alvo 1200, piso 900. Sem ela, o documento sai sem preço, o que é correto quando o preço já foi fechado e você só quer o cronograma
- `--atipica` — confirma que há feature atípica sem benchmark. A skill 1 não consegue avaliar isso sozinha porque depende da base dos últimos 8 projetos do núcleo; se você souber a resposta, passe a flag
- `--saida` — caminho do `validacao.json`

O script emite `validacao.json` e imprime um resumo com os avisos.

### 2. Ler os avisos antes de escrever qualquer coisa

Os avisos não são decoração — cada um corresponde a algo que muda o que o documento deve dizer:

| Aviso | O que fazer |
|---|---|
| Feature L/XL/XXL sem confirmação | Liste nominalmente na seção de dimensionamento. Um número montado sobre features não confirmadas não é um número fechado |
| Feature em XXL | Quebra obrigatória. O documento não deveria sair antes disso |
| Multiplicador acima de 2,0 | O projeto não é dimensionável em escopo fechado. Registre e escale ao CP |
| Mais de 10% em "A definir" | Escopo fechado não se sustenta. Diga isso no documento |
| Fator de buffer não resolvido | O buffer emitido está subestimado. Declare qual fator ficou de fora |
| Dependência apontando para fora da contagem | O cronograma ignorou essa dependência. Pode estar errado |

Aviso que você não entende é motivo para parar e perguntar, não para omitir.

### 3. Escrever o documento

Estrutura fixa em `references/template.md`. Sete seções, nesta ordem, sempre — é a padronização que justifica a skill existir.

O que você escreve: o parecer de consultoria (vem do `dimensionamento.json`, seção `parecer`), os objetivos de cada sprint, a leitura do delta, e a arquitetura. O que você copia do `validacao.json` sem alterar: todos os números, o cronograma e as conversões.

### 4. Gerar o PDF

Escreva o documento em Markdown primeiro, mostre ao usuário, e só depois converta. Para a conversão, use a skill `pdf` — ela cuida do layout e evita reinventar pipeline de renderização.

Nomeie `validacao-<cliente-slug>-<AAAA-MM-DD>.pdf`.

## A seção que justifica tudo

A seção 6, **Delta**, é a razão de esta skill existir.

No núcleo, o coordenador de negócios costuma validar o projeto **depois** de vendê-lo. Preço e prazo já foram ditos ao cliente. Isso significa que o documento não é um orçamento — é a medida honesta do que foi prometido, para que a equipe de projetos não descubra o buraco depois de já estar dentro dele.

Quando `delta.delta_semanas` é positivo, o documento precisa registrar **uma** destas saídas, com nome de quem decidiu:

1. **Cortar escopo** — quais features, quantos PD, quem aprovou
2. **Negociar sprints adicionais** — quantas, com quem, status
3. **Consumir margem** — quanto, quanto sobra
4. **Aceitar o risco** — quem aceitou e o que acontece se estourar

Sem uma dessas marcada, a validação não fecha. A trava existe porque, na ausência dela, a saída default é a quinta: a equipe absorve em silêncio e ninguém registra. Foi assim que projetos chegaram a 213% de taxa de execução.

Repare também na linha de **ITIP implícito**. Ela traduz atraso em dinheiro, e costuma ser a informação mais persuasiva do documento inteiro: um projeto pode ter sido bem precificado no cronograma otimista e cair para o piso no prazo real. O preço não estava errado — ele só valia num prazo que não vai acontecer.

## Regras do cronograma

Estão implementadas no script; você precisa conhecê-las para explicar o documento a quem perguntar. O raciocínio por trás de cada uma está em `references/algoritmo.md`.

- **Sprint é sempre 15 dias.** Bloco fracionário descreve quanto da sprint ele consome, não uma sprint mais curta
- Blocos fixos fracionários **dividem sprint**: discovery de 0,5 e infra de 0,5 ocupam a mesma
- Features entram por **ordem topológica de dependência**, depois MoSCoW, depois PD decrescente, e o id como desempate
- Feature nunca cai numa sprint anterior ou igual à de uma dependência
- Feature maior que a capacidade ocupa a sprint sozinha e a estoura — **visível de propósito**
- A **margem contratada** aparece como sprints próprias no fim, sem trabalho alocado

Essa última é uma escolha, e vale saber defendê-la: o cliente vê a data que está comprando e a equipe vê que margem é margem. A alternativa — diluir o buffer nas sprints — esconde a margem, e ela é consumida sem ninguém perceber.

## O que nunca fazer

| Nunca | Porque |
|---|---|
| Recalcular sprints, semanas ou preço no texto | O script é a única fonte. Duas fontes discordam e ninguém sabe qual vale |
| Ajustar o cronograma para caber no prazo vendido | O delta é o produto principal do documento |
| Omitir aviso do script | Cada aviso muda o que o documento deve dizer |
| Apresentar cronograma sem o buffer aplicado | É o erro do formato antigo: o risco ficava em prosa embaixo da tabela e a tabela virava o plano |
| Fechar com delta positivo e nenhuma saída marcada | É a trava que protege a equipe de projetos |
| Mudar a ordem das sete seções | A padronização é o produto |

## Arquivos

- **`scripts/calcular.py`** — o motor determinístico. Leia a docstring antes de mexer
- **`references/template.md`** — as sete seções, campo a campo
- **`references/algoritmo.md`** — por que o algoritmo é assim, e o que ele não resolve
