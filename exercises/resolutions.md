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

## 2) Solucao do Exercicio 2: tabela DriverSummary

Crie a tabela calculada DriverSummary:

```DAX
DriverSummary =
VAR Base =
    SUMMARIZE(
        LapTimes,
        LapTimes[grand_prix],
        LapTimes[session],
        LapTimes[driver]
    )
RETURN
    FILTER(
        ADDCOLUMNS(
            Base,
            "total_laps", CALCULATE(COUNTROWS(LapTimes)),
            "avg_speed_kmh", ROUND(CALCULATE(AVERAGE(LapTimes[avg_speed_kmh])), 3),
            "top_speed_kmh", ROUND(CALCULATE(MAX(LapTimes[top_speed_kmh])), 3),
            "max_throttle_pct", ROUND(CALCULATE(MAX(LapTimes[max_throttle_pct])), 3),
            "brake_samples", CALCULATE(SUM(LapTimes[brake_samples])),
            "avg_lap_time_s", ROUND(CALCULATE(AVERAGE(LapTimes[lap_time_s])), 3)
        ),
        [total_laps] > 0
    )
```

Observacao didatica:
- Essa tabela funciona bem para cards executivos, porque resume a performance do piloto por sessao.

Validacao sugerida no relatorio:
- Cards com avg_speed_kmh, top_speed_kmh e avg_lap_time_s.
- Tabela por driver para conferir os totais.

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

## 4) Solucao do Exercicio 4: tabela CircuitMap

Crie a tabela calculada CircuitMap:

```DAX
CircuitMap =
SELECTCOLUMNS(
    FILTER(
        FastestLapTelemetry,
        NOT ISBLANK([x]) && NOT ISBLANK([y])
    ),
    "grand_prix", [grand_prix],
    "session", [session],
    "driver", [driver],
    "lap", [lap],
    "distance", ROUND([distance], 3),
    "x", ROUND([x], 3),
    "y", ROUND([y] * -1, 3),
    "z", ROUND([z], 3),
    "speed_kmh", ROUND([speed], 3)
)
```

Observacao didatica:
- A inversao do eixo y ajuda a reproduzir o sentido visual do traçado da pista no scatter.

Validacao sugerida no relatorio:
- Scatter com x e y e cor por speed_kmh.
- Ajuste da ordem de camadas para deixar o tracado legivel.

## 5) Solucao do Exercicio 5: tabela DriverBattle

Crie a tabela calculada DriverBattle:

```DAX
DriverBattle =
VAR Base =
    SUMMARIZE(
        LapTimes,
        LapTimes[grand_prix],
        LapTimes[session],
        LapTimes[driver]
    )
RETURN
    ADDCOLUMNS(
        Base,
        "best_lap_time_s", ROUND(CALCULATE(MIN(LapTimes[lap_time_s])), 3),
        "avg_lap_time_s", ROUND(CALCULATE(AVERAGE(LapTimes[lap_time_s])), 3),
        "lap_count", CALCULATE(COUNTROWS(LapTimes)),
        "avg_speed_kmh", ROUND(CALCULATE(AVERAGE(LapTimes[avg_speed_kmh])), 3),
        "delta_to_session_best_s",
            ROUND(
                CALCULATE(MIN(LapTimes[lap_time_s])) -
                CALCULATE(
                    MIN(LapTimes[lap_time_s]),
                    ALLEXCEPT(
                        LapTimes,
                        LapTimes[grand_prix],
                        LapTimes[session]
                    )
                ),
                3
            )
    )
```

Observacao didatica:
- Essa tabela e a base para comparar ritmo entre pilotos na mesma sessao.

Validacao sugerida no relatorio:
- Matriz com driver, best_lap_time_s e delta_to_session_best_s.
- Ordenacao crescente por best_lap_time_s para destacar o piloto mais rapido.
