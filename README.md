# EntregasEditalAI — Validação e dimensionamento de projetos

Skills do Núcleo de Tecnologia e Inovação da Poli Júnior para transformar material bruto de um projeto em um dimensionamento auditável e num documento de validação padronizado.

## O problema que isso resolve

O núcleo dimensiona projetos hoje por prompt gigante, que muda conforme o anexo e o contexto. O problema dele não é qualidade — é **variância**. Duas validações do mesmo projeto saem diferentes, e validações que não se comparam entre si não calibram nada.

Na base histórica, a taxa de execução real média foi de 70,81% contra 107,23% prevista, com apenas 3 de 10 projetos dentro da faixa saudável de 85–105%.

Estas skills não precisam ser mais inteligentes que o prompt que substituem. Precisam ser **repetíveis**, rastreáveis até a fonte, e honestas sobre o que não sabem.

## As duas skills

| Skill | Entrada | Saída |
|---|---|---|
| **`dimensionar-projeto-ntec`** | Transcrição de reunião, protótipo do Lovable, notas do CN | Parecer de consultoria, features pontuadas em PD, multiplicador, riscos, lacunas → `dimensionamento.json` |
| **`documento-validacao-ntec`** | `dimensionamento.json` | Cronograma vendido sprint a sprint, delta vendido-vs-dimensionado, PDF de validação |

Elas se comunicam por um artefato intermediário, o `dimensionamento.json`, especificado em [`dimensionar-projeto-ntec/references/contrato.md`](dimensionar-projeto-ntec/references/contrato.md). É esse contrato que permite as duas evoluírem sem quebrar uma à outra.

## Princípios de desenho

**A skill 1 produz entradas; a skill 2 produz números.** Sprints, semanas, preço e ITIP são derivados e vivem só na skill 2. Se um número calculado viajasse no JSON, as duas poderiam discordar e não haveria como saber qual está certa.

**O cronograma é aritmética, não inferência.** A alocação de features em sprints é ordenação topológica por dependência, MoSCoW dentro de cada nível, e empacotamento guloso até a capacidade. Duas execuções com a mesma entrada precisam dar o mesmo cronograma — se não derem, o desenho está errado.

**Lacuna é entregável, não falha.** Diante de um campo sem evidência, um prompt grande preenche com o que é plausível — e plausível parece certo. A lista de lacunas vira a pauta da próxima call do CN, e vale mais que um campo preenchido por adivinhação.

**Complexidade alta exige confirmação humana.** Toda feature em L, XL ou XXL sai com `confirmado_por: null`. A skill propõe, um dev da stack confirma. É onde o erro custa caro em valor absoluto: errar uma XS em 100% custa 1 PD; errar uma XL em 30% custa 4.

## Estado

**Protótipo, v0.2.** Os coeficientes marcados 🟡 nos arquivos de referência são chute inicial ancorado na base histórica e **não estão calibrados**. A velocidade de 14 PD/sprint em particular é a junta mais frágil do sistema — é o único elo cujo erro contamina tudo de forma proporcional.

O `calcular.py` ainda **não foi executado** contra um dimensionamento real. Antes do primeiro uso para valer, rode o teste de determinismo: duas execuções no mesmo arquivo, comparadas com `fc` no Windows.

Três condições ainda abertas, documentadas em [`docs/premissa-validacao-metrificada.md`](docs/premissa-validacao-metrificada.md):

1. A fórmula exata da TE na planilha de controle não foi confirmada. Se for escopo entregue sobre tempo decorrido, a direção do diagnóstico inverte
2. A velocidade precisa ser medida, não suposta
3. A fronteira entre multiplicador e buffer precisa estar escrita — multiplicador mede mais trabalho, buffer mede incerteza sobre o trabalho

## Documentos

- [`docs/spec-documento-validacao.md`](docs/spec-documento-validacao.md) — o template do documento de validação, campo a campo, e as regras de alocação de sprint
- [`docs/premissa-validacao-metrificada.md`](docs/premissa-validacao-metrificada.md) — por que essa arquitetura constitui base para validação metrificada, e sob quais condições

## Como usar

As skills seguem o formato de skills do Claude. Instale copiando a pasta da skill para o diretório de skills do seu ambiente, ou empacote com o `skill-creator`.

Ponto de partida para entender a skill 1: leia `SKILL.md`, depois `references/exemplo.md`, que mostra um caso pequeno resolvido de ponta a ponta.

## Premissas fixas do núcleo

| Premissa | Valor |
|---|---|
| Sprint | 15 dias, sempre |
| Equipe padrão | 1 AS/PM + 2 devs |
| Dedicação efetiva | 3h/dia (faixa 2–4h) |
| 1 PD | 1 dia-dev útil a 3h |
| Velocidade base | 14 PD/sprint 🟡 |
| Escala | XS 1 · S 2 · M 5 · L 8 · XL 13 · XXL 21 |
| Buffer | base 15%, +5% por fator, teto 40% |
| Multiplicador | teto 2,0 |
