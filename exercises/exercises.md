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

## Exercicio 2: Criar Medidas para Cards Executivos

### Objetivo
Criar medidas que alimentem os cards executivos do painel de visao geral sem precisar materializar uma nova tabela.

### Requisitos
Crie medidas para:
- melhor volta geral
- velocidade media
- velocidade maxima
- tempo medio de volta
- piloto da melhor volta

### Regras
1. Use a tabela LapTimes criada no Exercicio 1 como base.
2. As medidas devem responder ao contexto de filtro de GP, sessao e piloto.
3. Arredonde os resultados numericos para 3 casas decimais quando fizer sentido.

### Entregaveis
1. DAX das medidas.
2. Cards no relatorio para mostrar: melhor volta geral, velocidade maxima, velocidade media e piloto da melhor volta.

---

## Exercicio 3: Criar Tabela da Volta Mais Rapida

### Objetivo
Criar uma tabela com os pontos de telemetria da volta mais rapida para montar os graficos de velocidade, throttle, brake e DRS.

### Requisitos
Crie uma tabela calculada chamada FastestLapTelemetry com as colunas:
- grand_prix
- session
- driver
- lap
- time
- distance
- rel_distance
- speed
- throttle
- brake
- drs
- x
- y
- z

### Regras
1. Identifique a volta com menor lap_time_s na tabela LapTimes.
2. Filtre a tabela Telemetry para retornar apenas os registros dessa volta.
3. Ordene a visualizacao por time ou distance, conforme o grafico.
4. Arredonde as metricas numericas para 3 casas decimais.

### Entregaveis
1. DAX da tabela FastestLapTelemetry.
2. Grafico de linha para speed e throttle ao longo da volta.
3. Grafico adicional para brake e DRS.
4. Base para o mapa do circuito com x e y.

---

## Exercicio 4: Criar Coluna Auxiliar para o Mapa do Circuito

### Objetivo
Criar uma coluna auxiliar para inverter o eixo y e facilitar o desenho do traçado do circuito.

### Requisitos
Adicione uma coluna calculada chamada y_inverted na tabela FastestLapTelemetry.

### Regras
1. Use a tabela FastestLapTelemetry como base.
2. A coluna deve inverter o eixo y para reproduzir o sentido visual do circuito.
3. Mantenha x, y_inverted e speed para o scatter.

### Entregaveis
1. DAX da coluna y_inverted.
2. Scatter plot com x e y_inverted representando o mapa do circuito.
3. Cor do ponto baseada em speed ou driver.

---

## Exercicio 5: Criar Medidas para Comparativo entre Pilotos

### Objetivo
Criar medidas para comparar o ritmo medio e o melhor tempo de volta entre pilotos na mesma sessao.

### Requisitos
Crie medidas para:
- melhor tempo de volta
- tempo medio de volta
- quantidade de voltas
- velocidade media
- delta para a melhor volta da sessao

### Regras
1. Use a tabela LapTimes como base.
2. As medidas devem funcionar em uma matriz com piloto nas linhas e sessao em filtro.
3. delta_to_session_best_s deve medir a diferenca do melhor tempo do piloto para o melhor tempo da sessao.
4. Arredonde as metricas numericas para 3 casas decimais.

### Entregaveis
1. DAX das medidas.
2. Visual de matriz ou tabela com ranking de pilotos por sessao.
3. Grafico para comparar ritmo e delta em relacao ao melhor da sessao.
