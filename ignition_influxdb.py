# Load dependencies.
from dotenv import load_dotenv
import os
import psycopg2
import time
import redis

# Class for processing data from Ignition PostgreSQL database and printing in InfluxDB Line Protocol.
class Historizer:

  # Redis key for the last processed timestamp.
  END_TIME_KEY = "ignition_influxdb_end_time"

  # Offset from current timestamp (in milliseconds) to avoid missing data.
  MS_OFFSET = -10000

  # Constructor. Establishes connections to PostgreSQL and Redis.   
  def __init__(self):

    # Connect to PostgreSQL and Redis.
    self.pgsql_conn = psycopg2.connect(
      dbname=os.getenv("IGNITION_INFLUXDB_PGSQL_DB_NAME"), 
      user=os.getenv("IGNITION_INFLUXDB_PGSQL_USER"), 
      password=os.getenv("IGNITION_INFLUXDB_PGSQL_PASSWORD"), 
      host=os.getenv("IGNITION_INFLUXDB_PGSQL_HOST"), 
      port=os.getenv("IGNITION_INFLUXDB_PGSQL_PORT")
    )
    self.redis_conn = redis.Redis(
      host=os.getenv("IGNITION_INFLUXDB_REDIS_HOST"), 
      port=int(os.getenv("IGNITION_INFLUXDB_REDIS_PORT")), 
      password=os.getenv("IGNITION_INFLUXDB_REDIS_PASSWORD")
    )

    # Read and store bucket name.
    self.bucket = os.getenv("IGNITION_INFLUXDB_INFLUXDB_BUCKET")

    # Configure translation table for InfluxDB Line Protocol.
    self.lp_trans = str.maketrans({",": "\\,", "=": "\\=", " ": "\\ "})

  # Destructor. Closes PostgreSQL connection.
  def __del__(self):
    self.pgsql_conn.close()

  # Process data from PostgreSQL and print in InfluxDB Line Protocol.
  def process(self):

    # Determine the start and end times for data retrieval.
    self.end_time = int(time.time() * 1000) + self.MS_OFFSET
    self.start_time = int(self.redis_conn.get(self.END_TIME_KEY) or -1) + 1

    # Retrieve tables that contain data in the calculated period.
    self.tables = self.get_tables()

    # Process data from each table.
    for table in self.tables:
      self.get_data(table)

    # Update the last processed timestamp.
    self.redis_conn.set(self.END_TIME_KEY, str(self.end_time))

  # Retrieve tables that contain data in the calculated period.
  def get_tables(self):

    # Retrieve tables that contain data in the calculated period.
    cur = self.pgsql_conn.cursor()
    cur.execute("""
      SELECT 
        DISTINCT pname
      FROM 
        sqlth_partitions
      WHERE
        (start_time <= %(end_time)s AND end_time >= %(start_time)s) OR
        (start_time BETWEEN %(start_time)s AND %(end_time)s) OR
        (end_time BETWEEN %(start_time)s AND %(end_time)s)
      GROUP BY 
        pname;
    """, {'start_time': self.start_time, 'end_time': self.end_time})
    tables = cur.fetchall()
    cur.close()

    # Return list of table names.
    return [table[0] for table in tables]

  # Retrieve data from the specified table.
  def get_data(self, table):

    # Configure query for retrieving data from the specified table.
    query = """
      SELECT 
        sqlth_te.tagpath,
        sqlth_te.datatype,
        {table}.intvalue, 
        {table}.floatvalue, 
        {table}.t_stamp
      FROM 
        {table}
      JOIN 
        sqlth_te ON {table}.tagid = sqlth_te.id
      WHERE
        {table}.t_stamp BETWEEN %s AND %s AND
        sqlth_te.datatype != %s;
    """.format(table=table)
  
    # Retrieve data from the specified table.
    with self.pgsql_conn.cursor() as cur:
      cur.execute(query, (self.start_time, self.end_time, 2))
      rows = cur.fetchall()

    # Format and print each row.
    for row in rows:
      self.format_and_print_row(row)

  # Format and print the row in InfluxDB Line Protocol.
  def format_and_print_row(self, row):

    # Format and print the row in InfluxDB Line Protocol.
    try:
      print(f"{self.bucket},tagpath={row[0].translate(self.lp_trans)} value={float(row[2]) if row[1] == 0 else float(row[3])} {row[4]}000000")
    except Exception:
      return

# Load environment variables from .env file.
load_dotenv()

# Create Historizer object.
obj = Historizer()

# Process data every 5 seconds.
while True:
  obj.process()
  time.sleep(5)