# Ingition-InfluxDB Bridge

This relatively simple Python script is designed to pull data from a PostgreSQL database populated by Ignition via its Historian module and format that data for insertion into InfluxDB.

I'm using this program in production and it works well for me, but I'm not a professional Python programmer so I'm sure there are improvements that could be made. Let me know if you have any suggestions!

## How it Works

```mermaid
flowchart TB
  subgraph PLC["PLCs"]
  direction TB
  PLC1["fa:fa-microchip PLC"]
  PLC2["fa:fa-microchip PLC"]
  PLC3["fa:fa-microchip PLC"]
  end
  subgraph InfluxDB["InfluxDB Cluster"]
  direction LR
  InfluxDB1[("fa:fa-database InfluxDB #1")]
  InfluxDB2[("fa:fa-database InfluxDB #2")]
  InfluxDBN[("fa:fa-database InfluxDB #n")]
  end
  PLC1 -- OPC UA --> Ignition("fa:fa-server Ignition")
  PLC2 -- OPC UA --> Ignition
  PLC3 -- OPC UA --> Ignition
  Ignition -- Publishes Via Historian Module --> PGSQL[("fa:fa-database PostgreSql")]
  PGSQL -- Data Retrieved By --> Bridge(["fab:fa-python Ignition-InfluxDB Bridge"])
  Bridge -- Process Managed By --> Telegraf("fa:fa-server Telegraf")
  Telegraf -- Pushes Data To --> InfluxDB
  InfluxDB1 <-- Mirrored --> InfluxDB2
  InfluxDB2 <-- Mirrored --> InfluxDBN
  style Bridge fill:#FF6D00,stroke:#000000,color:#FFFFFF
```