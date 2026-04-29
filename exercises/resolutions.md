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
VAR Base =
    SUMMARIZE(
        Telemetry,
        Telemetry[grand_prix],
        Telemetry[session],
        Telemetry[driver],
        Telemetry[lap],
        "lap_time_s_raw", MAX(Telemetry[time]) - MIN(Telemetry[time]),
        "avg_speed_kmh_raw", AVERAGE(Telemetry[speed]),
        "top_speed_kmh_raw", MAX(Telemetry[speed]),
        "max_throttle_pct_raw", MAX(Telemetry[throttle]),
        "brake_samples", SUMX(Telemetry, IF(Telemetry[brake] > 0, 1, 0))
    )
RETURN
    FILTER(
        ADDCOLUMNS(
            Base,
            "lap_time_s", ROUND([lap_time_s_raw], 3),
            "avg_speed_kmh", ROUND([avg_speed_kmh_raw], 3),
            "top_speed_kmh", ROUND([top_speed_kmh_raw], 3),
            "max_throttle_pct", ROUND([max_throttle_pct_raw], 3)
        ),
        [lap_time_s_raw] > 0
    )
```

Observacao didatica:
- Se preferir, o professor pode remover as colunas com sufixo raw depois.

Validacao sugerida no relatorio:
- Visual de tabela com grand_prix, session, driver, lap, lap_time_s.
- Ordenar por lap_time_s ascendente e mostrar Top N = 10.

## 2) Solucao do Exercicio 2: FastestLapTelemetry

Passo 1. Criar tabela auxiliar com ranking da melhor volta por piloto na corrida:

```DAX
RaceLapRank =
VAR RaceLaps =
    FILTER(LapTimes, LapTimes[session] = "Race")
RETURN
    ADDCOLUMNS(
        RaceLaps,
        "lap_rank_per_driver",
            RANKX(
                FILTER(
                    RaceLaps,
                    [grand_prix] = EARLIER([grand_prix])
                        && [session] = EARLIER([session])
                        && [driver] = EARLIER([driver])
                ),
                [lap_time_s],
                ,
                ASC,
                DENSE
            )
    )
```

Passo 2. Criar a tabela com telemetria somente da volta rank 1:

```DAX
FastestLapTelemetry =
VAR BestLaps =
    FILTER(RaceLapRank, [lap_rank_per_driver] = 1)
RETURN
    NATURALINNERJOIN(
        ADDCOLUMNS(
            Telemetry,
            "lap_progress_pct", ROUND(Telemetry[rel_distance] * 100, 3)
        ),
        SELECTCOLUMNS(
            BestLaps,
            "grand_prix", [grand_prix],
            "session", [session],
            "driver", [driver],
            "lap", [lap],
            "lap_time_s", [lap_time_s],
            "lap_rank_per_driver", [lap_rank_per_driver]
        )
    )
```

Validacao 1: pontos de telemetria por piloto

```DAX
TelemetryPoints = COUNTROWS(FastestLapTelemetry)
```

Coloque driver em linhas e a medida TelemetryPoints em valores.

Validacao 2: card para melhor volta geral da corrida

```DAX
BestLapTimeRace =
MINX(
    FILTER(LapTimes, LapTimes[session] = "Race"),
    LapTimes[lap_time_s]
)
```

```DAX
BestDriverRace =
VAR T =
    TOPN(
        1,
        FILTER(LapTimes, LapTimes[session] = "Race"),
        LapTimes[lap_time_s], ASC
    )
RETURN
    MAXX(T, LapTimes[driver])
```

## 3) Solucao do Exercicio 3: CircuitMapPoints para scatter

Crie a tabela calculada:

```DAX
CircuitMapPoints =
SELECTCOLUMNS(
    FastestLapTelemetry,
    "grand_prix", [grand_prix],
    "session", [session],
    "driver", [driver],
    "lap", [lap],
    "x", [x],
    "y", [y],
    "speed", [speed],
    "throttle", [throttle],
    "brake", [brake],
    "lap_progress_pct", [lap_progress_pct],
    "time", [time]
)
```

Configuracao do visual Scatter no Power BI:
1. Eixo X: x
2. Eixo Y: y
3. Legenda: driver ou faixa de speed
4. Tamanho: opcional (por exemplo throttle)
5. Tooltip: speed, brake, lap_progress_pct, time

Dica importante:
- No painel de formato, ajuste o eixo Y (inclusive reverso) se o circuito parecer invertido.
- Use filtro de driver para comparar traçados entre pilotos.

## 4) Bonus: tabelas para cards

Tabela por piloto com melhor volta:

```DAX
DriverFastestLapCard =
VAR BestPerDriver =
    FILTER(RaceLapRank, [lap_rank_per_driver] = 1)
RETURN
    NATURALLEFTOUTERJOIN(
        SELECTCOLUMNS(
            BestPerDriver,
            "driver", [driver],
            "grand_prix", [grand_prix],
            "session", [session],
            "lap", [lap],
            "lap_time_s", [lap_time_s],
            "top_speed_kmh", [top_speed_kmh]
        ),
        SELECTCOLUMNS(
            Drivers,
            "driver", Drivers[driver],
            "full_name", Drivers[fn] & " " & Drivers[ln],
            "team", Drivers[team]
        )
    )
```

Tabela com melhor volta geral da corrida:

```DAX
RaceFastestLapCard =
TOPN(
    1,
    FILTER(LapTimes, LapTimes[session] = "Race"),
    LapTimes[lap_time_s], ASC
)
```

## 5) Estrutura recomendada de paginas no relatorio

1. Pagina 1: Visao geral da corrida
- cards de melhor volta
- tabela Top 10 lap_time_s
2. Pagina 2: Telemetria da melhor volta
- linhas de speed por lap_progress_pct
- linha de throttle e brake
3. Pagina 3: Mapa do circuito
- scatter x por y
- segmentador de piloto
