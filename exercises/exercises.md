# Exercicios: Modelagem de Dados no Power BI (Australian Grand Prix)

Estes exercicios utilizam os arquivos:
- Australian_Grand_Prix/telemetry.csv
- Australian_Grand_Prix/drivers.csv

Objetivo geral: ensinar os alunos a criar novas tabelas no Power BI a partir da telemetria para alimentar graficos, cards e mapa de circuito.

## Preparacao

1. Importe os dois CSVs no Power BI Desktop (Obter Dados > Texto/CSV).
2. Nomeie as tabelas como:
- Telemetry
- Drivers
3. Confira os tipos de dados principais em Telemetry:
- time, rpm, speed, throttle, brake, drs, distance, rel_distance, acc_x, acc_y, acc_z, x, y, z: Numero decimal
- gear, lap: Numero inteiro
- grand_prix, session, driver, dataKey, DriverAhead: Texto
4. Crie relacionamento entre Drivers[driver] e Telemetry[driver] (1 para muitos).

---

## Exercicio 1: Criar Tabela de Voltas (Lap Times)

### Objetivo
Criar uma tabela com uma linha por volta (por piloto, sessao e GP), incluindo tempo da volta e metricas de desempenho.

### Requisitos
Crie uma tabela calculada chamada LapTimes com as colunas:
- grand_prix
- session
- driver
- lap
- lap_time_s
- avg_speed_kmh
- top_speed_kmh
- max_throttle_pct
- brake_samples

### Regras
1. lap_time_s deve ser calculado como MAX(time) - MIN(time) por volta.
2. Remova voltas invalidas com lap_time_s menor ou igual a 0.
3. Arredonde lap_time_s e velocidades para 3 casas decimais.

### Entregaveis
1. DAX da tabela LapTimes.
2. Tabela visual no relatorio com Top 10 voltas mais rapidas.

---

## Exercicio 2: Telemetria da Volta Mais Rapida para Graficos e Cards

### Objetivo
Criar uma tabela com os pontos de telemetria apenas da volta mais rapida de cada piloto na corrida.

### Requisitos
Crie uma tabela calculada chamada FastestLapTelemetry contendo:
- todas as colunas de Telemetry
- lap_time_s
- lap_rank_per_driver
- lap_progress_pct

### Regras
1. Use LapTimes como base.
2. Considere somente session igual a Race.
3. Para cada piloto, mantenha apenas a volta com menor lap_time_s.
4. Inclua lap_progress_pct como rel_distance multiplicado por 100.

### Entregaveis
1. DAX da tabela FastestLapTelemetry.
2. Visual de tabela com contagem de pontos por piloto.
3. Um card com piloto e tempo da volta mais rapida geral da corrida.

---

## Exercicio 3: Mapa do Circuito com Scatter (X e Y)

### Objetivo
Usar x e y da telemetria para montar o mapa do circuito em um grafico de dispersao.

### Requisitos
Crie uma tabela calculada chamada CircuitMapPoints com:
- grand_prix
- session
- driver
- lap
- x
- y
- speed
- throttle
- brake
- lap_progress_pct
- time

### Regras
1. Baseie-se na tabela FastestLapTelemetry.
2. Permita duas abordagens:
- apenas o piloto com melhor volta geral
- todos os pilotos, usando cor por piloto
3. Ordene os pontos por time para preservar o trajeto da volta.

### Entregaveis
1. DAX da tabela CircuitMapPoints.
2. Grafico Scatter com:
- eixo X: x
- eixo Y: y
- cor: speed ou driver
- dica: se o circuito parecer espelhado, testar inverter o eixo Y no visual

---

## Bonus (Opcional)

1. Criar tabela DriverFastestLapCard com uma linha por piloto:
- driver, nome completo, equipe, melhor volta, velocidade maxima na melhor volta
2. Criar tabela RaceFastestLapCard com uma unica linha:
- piloto mais rapido da corrida, numero da volta, tempo da volta
