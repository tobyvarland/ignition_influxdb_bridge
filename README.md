# Ingition-InfluxDB Bridge

This relatively simple Python script is designed to pull data from a PostgreSQL database populated by Ignition via its Historian module and format that data for insertion into InfluxDB.

I'm using this program in production and it works well for me, but I'm not a professional Python programmer so I'm sure there are improvements that could be made. Let me know if you have any suggestions!

## How it Works

```mermaid
flowchart LR
 subgraph PLC["PLCs"]
    direction TB
        PLC1("PLC")
        PLC2("PLC")
        PLC3("PLC")
  end
 subgraph InfluxDB["InfluxDB Cluster"]
    direction TB
        InfluxDB1[("InfluxDB #1")]
        InfluxDB2[("InfluxDB #2")]
        InfluxDBN[("InfluxDB #n")]
  end
    PLC1 --> Ignition("Ignition")
    PLC2 --> Ignition
    PLC3 --> Ignition
    Ignition --> PGSQL[("PostgreSql")]
    PGSQL --> Bridge(["Ignition-InfluxDB Bridge"])
    Bridge --> Telegraf("Telegraf")
    Telegraf --> InfluxDB
    InfluxDB1 <---> InfluxDB2
    InfluxDB2 <---> InfluxDBN
    classDef basic fill:#ffffff,stroke:#cccccc,stroke-width:3px,color:#000000,font-weight:bold;
    classDef bridge fill:#df151a,stroke:#000000,stroke-width:3px,color:#ffffff,font-weight:bold;
    classDef box fill:#eeeeee,stroke:#aaaaaa,stroke-width:3px,color:#000000,font-weight:bold;
    class PLC1,PLC2,PLC3,Ignition,PGSQL,Telegraf,InfluxDB1,InfluxDB2,InfluxDBN basic;
    class Bridge bridge;
    class PLC,InfluxDB box;
```