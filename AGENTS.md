# Agent Guidelines for Kolada_Fabric

## Important: Timeout constraints in data fetch notebooks

The Kolada API returns very large volumes of data. Notebook `03_Fetch_Kolada_Data.ipynb` is particularly affected.

**CRITICAL RULE:** When fetching data from the Kolada API and writing to the Lakehouse, ALWAYS write data to the Lakehouse WITHIN each loop iteration (using `mode("append")`). NEVER collect all data in memory and write once at the end — the notebook will time out and all data will be lost.

The notebook must also support resuming after a timeout by checking what has already been written and skipping those batches on re-run.

## Batch Processing Pattern

Always use this pattern when fetching large volumes of data:

```python
# Check what's already been fetched
try:
    df_existing = spark.table("fKoladaData").select("kpi").distinct().toPandas()
    fetched_kpis = set(df_existing["kpi"].tolist())
except:
    fetched_kpis = set()

# Filter out already-fetched items
remaining_items = [k for k in ALL_ITEMS if k not in fetched_kpis]

# Process in batches
for i in range(0, len(remaining_items), BATCH_SIZE):
    batch = remaining_items[i:i+BATCH_SIZE]
    df_batch = fetch_data(batch, ...)
    
    if not df_batch.empty:
        spark_df = spark.createDataFrame(df_batch)
        spark_df.write.mode("append").format("delta").saveAsTable("fKoladaData")
```

## Microsoft Fabric Notebook Context

- A spark session is automatically available in Fabric notebooks
- DO NOT add `SparkSession.builder` or `spark.stop()` calls
- Use `spark.table()` to read from Lakehouse tables
- Use `.saveAsTable()` to write to Lakehouse tables
