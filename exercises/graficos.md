# Guia de Gráficos para o Dashboard de Formula 1 no Power BI

Este arquivo serve como referência para montar os backgrounds e também para orientar os alunos sobre quais visuais colocar em cada painel.

## 1. Painel de Visão Geral

### Objetivo
Dar a leitura executiva da corrida em poucos segundos.

### Visuais recomendados
- Card 1: Melhor volta da corrida
- Card 2: Piloto mais rápido
- Card 3: Velocidade máxima
- Card 4: Velocidade média
- Gráfico de colunas: tempo da melhor volta por piloto
- Linha ou área: velocidade ao longo da volta mais rápida

### Como montar
- Use os cards na faixa superior ou lateral direita.
- Deixe o gráfico principal ocupar a maior área central.
- Coloque o gráfico de colunas abaixo ou ao lado do gráfico principal, se houver espaço.

### Título sugerido dos cards
- Melhor volta
- Piloto líder
- Velocidade máxima
- Ritmo médio

---

## 2. Painel de Volta Mais Rápida

### Objetivo
Comparar o comportamento da melhor volta com foco em tempo e setores.

### Visuais recomendados
- Linha: tempo acumulado por distância ou por ponto da volta
- Linha: velocidade por distância
- Linha ou área: throttle e brake no mesmo gráfico
- Cartões pequenos: Setor 1, Setor 2, Setor 3

### Como montar
- O gráfico principal deve ser uma linha larga ocupando a maior parte do painel.
- Os cartões de setor devem ficar em bloco lateral ou em faixa inferior.
- Se quiser destacar uma volta específica, use segmentador de piloto e volta.

### Título sugerido dos cards
- Setor 1
- Setor 2
- Setor 3
- Tempo total

---

## 3. Painel de Telemetria

### Objetivo
Mostrar a leitura técnica do carro na volta mais rápida.

### Visuais recomendados
- Linha 1: speed ao longo do tempo ou da distância
- Linha 2: throttle ao longo do tempo ou da distância
- Linha 3: brake ao longo do tempo ou da distância
- Linha 4: DRS ou gear
- Card pequeno: pico de velocidade
- Card pequeno: maior frenagem

### Como montar
- Use um gráfico principal com speed como base.
- Coloque throttle e brake em visuais empilhados ou sobrepostos.
- Se preferir, use small multiples para cada métrica.

### Título sugerido dos cards
- Pico de velocidade
- Frenagem máxima
- Abertura de acelerador
- Uso de DRS

---

## 4. Painel do Mapa do Circuito

### Objetivo
Desenhar o traçado da pista com x e y da telemetria.

### Visuais recomendados
- Scatter: x no eixo X e y no eixo Y
- Cor: speed ou piloto
- Tamanho: throttle ou velocidade
- Tooltip: speed, throttle, brake, lap_progress_pct, time
- Card pequeno: piloto selecionado
- Card pequeno: melhor volta usada no mapa

### Como montar
- O scatter deve ocupar quase todo o painel.
- O eixo Y pode precisar ser invertido para o traçado ficar visualmente correto.
- Se houver comparação entre pilotos, use legenda por piloto e um slicer de driver.

### Título sugerido dos cards
- Traçado da pista
- Piloto selecionado
- Melhor volta usada
- Velocidade por ponto

---

## 5. Painel de Comparativo de Pilotos

### Objetivo
Comparar ritmo, consistência e diferença de performance entre pilotos.

### Visuais recomendados
- Linha: diferença para a melhor volta
- Linha: velocidade por piloto
- Barras: melhor volta por piloto
- Matriz ou tabela: piloto, equipe, volta, tempo, velocidade máxima
- Card pequeno: delta para o líder
- Card pequeno: posição atual

### Como montar
- Deixe o gráfico principal mostrando a comparação entre 2 a 4 pilotos.
- Use um segundo gráfico menor para ranking ou stint.
- Se houver pouco espaço, priorize linha de delta e ranking.

### Título sugerido dos cards
- Delta para o líder
- Posição atual
- Melhor stint
- Consistência

---

## 6. Painéis adicionais úteis

### Estratégia de corrida
Visuais:
- barras empilhadas por stint
- linha de posição ao longo das voltas
- cartões com número de pit stops e volta do pit

### Desempenho por equipe
Visuais:
- barras por equipe
- cards com melhor volta da equipe
- tabela com piloto e equipe

### Comparação entre sessões
Visuais:
- slicer para Practice, Qualifying, Race
- linhas de speed e lap time por sessão
- matriz resumo por sessão

---

## Padrão visual recomendado para os backgrounds

Para os backgrounds dos painéis, a melhor composição é:
- topo com uma faixa pequena de título
- centro ocupando a maior área possível para o gráfico principal
- bloco lateral ou inferior para cards menores
- espaço livre suficiente para o usuário encaixar os visuais sem esconder os textos

A regra prática é simples:
- título pequeno e discreto
- destaque forte para o espaço do gráfico
- cards secundários claramente delimitados
- linguagem visual agressiva, limpa e com cara de Formula 1
