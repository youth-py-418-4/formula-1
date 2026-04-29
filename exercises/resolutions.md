# Resolucao: Exercicios Power BI (Australian Grand Prix)

Este arquivo traz uma resolucao completa em Power BI usando DAX.

## 0) Preparacao no modelo

1. Importe:
- Australian_Grand_Prix/telemetry.csv como Telemetry
- Australian_Grand_Prix/drivers.csv como Drivers
2. Crie relacionamento:
- Drivers[driver] (1) para Telemetry[driver] (N)
3. Confirme tipos numericos em Telemetry para colunas de medicao e coordenadas.

## 1) Solucao do Exercicio 1: tabela LapTimes

Crie a tabela calculada LapTimes:

```DAX
LapTimes =
    SUMMARIZE(
        Telemetry,
        Telemetry[grand_prix],
        Telemetry[session],
        Telemetry[driver],
        Telemetry[lap],
        "lap_time_s", MAX(Telemetry[time]),
        "avg_speed_kmh", AVERAGE(Telemetry[speed]),
        "top_speed_kmh", MAX(Telemetry[speed]),
        "max_throttle_pct", MAX(Telemetry[throttle]),
        "brake_samples", SUMX(Telemetry, IF(Telemetry[brake] > 0, 1, 0))
    )
```

Observacao didatica:
- Se preferir, o professor pode remover as colunas com sufixo raw depois.

Validacao sugerida no relatorio:
- Visual de tabela com grand_prix, session, driver, lap, lap_time_s.
- Ordenar por lap_time_s ascendente e mostrar Top N = 10.

## 2) Solucao do Exercicio 2: medidas para cards executivos

Crie as medidas abaixo:

```DAX
Best Lap Time (s) =
MIN(LapTimes[lap_time_s])

Average Speed (km/h) =
AVERAGE(LapTimes[avg_speed_kmh])

Top Speed (km/h) =
MAX(LapTimes[top_speed_kmh])

Average Lap Time (s) =
AVERAGE(LapTimes[lap_time_s])

Fastest Driver =
VAR BestRow =
    TOPN(
        1,
        FILTER(LapTimes, LapTimes[lap_time_s] > 0),
        LapTimes[lap_time_s], ASC,
        LapTimes[driver], ASC
    )
RETURN
    MAXX(BestRow, LapTimes[driver])
```

Observacao didatica:
- Essas medidas funcionam bem para cards executivos, porque respeitam o contexto de filtro da pagina.

Validacao sugerida no relatorio:
- Cards com Best Lap Time (s), Average Speed (km/h), Top Speed (km/h) e Fastest Driver.

## 3) Solucao do Exercicio 3: tabela FastestLapTelemetry

Crie a tabela calculada FastestLapTelemetry:

```DAX
FastestLapTelemetry =
VAR BestLapRow =
    TOPN(
        1,
        FILTER(
            LapTimes,
            LapTimes[lap_time_s] > 0
        ),
        LapTimes[lap_time_s], ASC,
        LapTimes[grand_prix], ASC,
        LapTimes[session], ASC,
        LapTimes[driver], ASC,
        LapTimes[lap], ASC
    )
VAR BestGrandPrix = MAXX(BestLapRow, LapTimes[grand_prix])
VAR BestSession = MAXX(BestLapRow, LapTimes[session])
VAR BestDriver = MAXX(BestLapRow, LapTimes[driver])
VAR BestLap = MAXX(BestLapRow, LapTimes[lap])
RETURN
    SELECTCOLUMNS(
        FILTER(
            Telemetry,
            Telemetry[grand_prix] = BestGrandPrix &&
            Telemetry[session] = BestSession &&
            Telemetry[driver] = BestDriver &&
            Telemetry[lap] = BestLap
        ),
        "grand_prix", Telemetry[grand_prix],
        "session", Telemetry[session],
        "driver", Telemetry[driver],
        "lap", Telemetry[lap],
        "time", ROUND(Telemetry[time], 3),
        "distance", ROUND(Telemetry[distance], 3),
        "rel_distance", ROUND(Telemetry[rel_distance], 3),
        "speed", ROUND(Telemetry[speed], 3),
        "throttle", ROUND(Telemetry[throttle], 3),
        "brake", ROUND(Telemetry[brake], 3),
        "drs", ROUND(Telemetry[drs], 3),
        "x", ROUND(Telemetry[x], 3),
        "y", ROUND(Telemetry[y], 3),
        "z", ROUND(Telemetry[z], 3)
    )
```

Observacao didatica:
- Use essa tabela para os graficos de linha e area da volta mais rapida.

Validacao sugerida no relatorio:
- Grafico de linha com time no eixo X e speed no eixo Y.
- Grafico com throttle e brake na mesma pagina.

## 4) Solucao do Exercicio 4: coluna y_inverted

Adicione uma coluna calculada y_inverted na tabela FastestLapTelemetry:

```DAX
y_inverted = -FastestLapTelemetry[y]
```

Observacao didatica:
- A inversao do eixo y ajuda a reproduzir o sentido visual do traçado da pista no scatter.

Validacao sugerida no relatorio:
- Scatter com x e y_inverted e cor por speed.
- Ajuste da ordem de camadas para deixar o tracado legivel.

## 5) Solucao do Exercicio 5: medidas para comparativo entre pilotos

Crie as medidas abaixo:

```DAX
Best Lap Time (s) =
MIN(LapTimes[lap_time_s])

Average Lap Time (s) =
AVERAGE(LapTimes[lap_time_s])

Lap Count =
COUNTROWS(LapTimes)

Average Speed (km/h) =
AVERAGE(LapTimes[avg_speed_kmh])

Delta to Session Best (s) =
VAR DriverBest = MIN(LapTimes[lap_time_s])
VAR SessionBest =
    CALCULATE(
        MIN(LapTimes[lap_time_s]),
        ALLEXCEPT(
            LapTimes,
            LapTimes[grand_prix],
            LapTimes[session]
        )
    )
RETURN
    ROUND(DriverBest - SessionBest, 3)
```

Observacao didatica:
- Essas medidas funcionam melhor do que uma tabela porque respeitam o filtro de sessao e piloto.

Validacao sugerida no relatorio:
- Matriz com driver nas linhas e as medidas de best lap, delta e velocidade nos valores.
- Ordenacao crescente por Best Lap Time (s) para destacar o piloto mais rapido.
