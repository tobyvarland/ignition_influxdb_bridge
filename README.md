# Ingition-InfluxDB Bridge

This relatively simple Python script is designed to pull data from a PostgreSQL database populated by Ignition via its Tag Historian module and format that data for insertion into InfluxDB.

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
  subgraph Telegraf["Telegraf w/ execd"]
  Bridge(["Ignition-InfluxDB Bridge"])
  end
    PLC1 --> Ignition("Ignition")
    PLC2 --> Ignition
    PLC3 --> Ignition
    Ignition --> PGSQL[("PostgreSql")]
    PGSQL --> Bridge
    Bridge --> InfluxDB1 & InfluxDB2 & InfluxDBN
    classDef basic fill:#ffffff,stroke:#cccccc,stroke-width:3px,color:#000000,font-weight:bold;
    classDef bridge fill:#df151a,stroke:#000000,stroke-width:3px,color:#ffffff,font-weight:bold;
    classDef box fill:#eeeeee,stroke:#aaaaaa,stroke-width:3px,color:#000000,font-weight:bold;
    class PLC1,PLC2,PLC3,Ignition,PGSQL,Telegraf,InfluxDB1,InfluxDB2,InfluxDBN basic;
    class Bridge bridge;
    class PLC,InfluxDB,Telegraf box;
```

### [Ignition Tag Historian](https://inductiveautomation.com/ignition/modules/tag-historian)

I'm not going to cover configuring Ignition, OPC UA connections, or a lot of details about configuring the Tag Historian module here. Ignition's documentation is much better than mine.

In my application, I have a separate server running PostgreSQL. I created a very simple connection to the database in Ignition using the PostgreSQL JDBC driver. In the tag history configuration, I specified partitioning data into single day tables (so that I'm querying smaller tables). I also enabled data pruning after 90 days since I'm using InfluxDB for long term data storage.

With that configured, I configure history on tags within Ignition Designer and trust that Ignition will do the work of getting the data into PostgreSQL.

Once the data is in PostgreSQL, the script dynamically retrieves a list of tables containing relevant data and then retrieves the data from that list of tables.

### [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) & [`execd`](https://github.com/influxdata/telegraf/blob/master/plugins/inputs/execd/README.md)

I'm using Telegraf's `execd` plugin as a process manager for running the Ignition-Influxdb Bridge. The Python script is set to run continuously (with a delay of 5 seconds between each loop), and `execd` handles restarting the script if it ever stops running. It's not a super elegant configuration, but it works in my application.

Telegraf is great because it can be configured to output data to multiple InfluxDB targets at the same time. I run two InfluxDB servers and write my data to both in order to handle downtime on either server. Telegraf makes that trivial. The Ingition-InfluxDB Bridge simply prints data in [InfluxDB Line Protocol](https://docs.influxdata.com/influxdb/v2/reference/syntax/line-protocol/) format and Telegraf handles the rest. This eliminates the need for the Ignition-InfluxDB Bridge to know anything about the InfluxDB servers or configuration.