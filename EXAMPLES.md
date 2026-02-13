# Example Configurations for Kolada Fabric

This file provides example configurations for different use cases.

## Example 1: Basic Municipality Performance Dashboard

For analyzing general municipality performance across Sweden:

```python
# In notebook 03_Fetch_Kolada_Data.ipynb

# Common performance KPIs
KPI_IDS = [
    "N00945",  # Example KPI 1
    "N00946",  # Example KPI 2
    # Add more KPI IDs after running notebook 01
]

# All municipalities (leave empty)
MUNICIPALITY_IDS = []

# Recent years
YEARS = ["2020", "2021", "2022", "2023"]
```

## Example 2: Specific Municipality Deep Dive

For detailed analysis of specific municipalities:

```python
# Focus on Stockholm, Göteborg, Malmö
MUNICIPALITY_IDS = ["0180", "1480", "1280"]

# All available KPIs (or filter by category after checking metadata)
KPI_IDS = []  # Will need to specify after reviewing KPI metadata

YEARS = ["2018", "2019", "2020", "2021", "2022", "2023"]
```

## Example 3: Education Sector Analysis

For education-focused KPIs:

```python
# Education KPIs (examples - check actual IDs in metadata)
KPI_IDS = [
    # Add education-related KPI IDs from notebook 01
    # Search for keywords: "skola", "elev", "utbildning"
]

# All municipalities
MUNICIPALITY_IDS = []

# Academic years
YEARS = ["2019", "2020", "2021", "2022", "2023"]
```

## Example 4: Healthcare/Social Services

For healthcare and social services analysis:

```python
# Healthcare KPIs (examples - check actual IDs in metadata)
KPI_IDS = [
    # Add healthcare-related KPI IDs from notebook 01
    # Search for keywords: "vård", "äldreomsorg", "hälsa"
]

# All municipalities
MUNICIPALITY_IDS = []

YEARS = ["2020", "2021", "2022", "2023"]
```

## Example 5: Regional Comparison

For comparing regions (using municipality groups):

1. First, run notebook 02 to get municipality groups
2. Identify group IDs from `municipality_groups_metadata` table
3. Use group IDs instead of individual municipality IDs:

```python
KPI_IDS = ["N00945", "N00946"]  # Your KPIs of interest

# Use group IDs from municipality_groups_metadata
MUNICIPALITY_IDS = ["group_id_1", "group_id_2"]

YEARS = ["2020", "2021", "2022"]
```

## Example 6: Organizational Unit Analysis

For school or department level analysis:

```python
# In a customized version of notebook 03

# First get OU IDs from notebook 02
# Filter by municipality if needed

OU_KPI_IDS = [
    # KPIs that have OU data (check has_ou_data = true in KPI metadata)
]

OU_IDS = [
    # Specific organizational unit IDs from ou_metadata table
]

OU_YEARS = ["2020", "2021", "2022"]

# Use the fetch_ou_data function
df_ou_data = fetch_ou_data(OU_KPI_IDS, OU_IDS if OU_IDS else None, OU_YEARS)
```

## Configuration File Customization

You can also modify `config/config.json` for workspace settings:

```json
{
  "api_base_url": "http://api.kolada.se/v2",
  "lakehouse_name": "MyCustomLakehouse",
  "workspace_name": "MyAnalyticsWorkspace",
  "notebook_names": {
    "metadata_kpi": "01_Fetch_KPI_Metadata",
    "metadata_municipality": "02_Fetch_Municipality_Metadata",
    "data_ingestion": "03_Fetch_Kolada_Data"
  },
  "tables": {
    "kpi": "kpi_metadata",
    "municipality": "municipality_metadata",
    "data": "kolada_data_2023"
  },
  "pagination": {
    "per_page": 5000
  }
}
```

## Incremental Loading Strategy

For regular updates (future enhancement):

```python
# Use from_date parameter for incremental loads
from datetime import datetime, timedelta

# Get data changed in last 30 days
last_update = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

# Modify API calls to include from_date parameter
url = f"{API_BASE_URL}/data/kpi/{kpi_param}/year/{year_param}?per_page={PER_PAGE}&from_date={last_update}"
```

## Performance Optimization

For large datasets:

```python
# Strategy 1: Batch by year
for year in YEARS:
    df_year = fetch_kolada_data(KPI_IDS, MUNICIPALITY_IDS, [year])
    # Process and save each year separately
    df_year.write.format("delta").mode("append").save(table_path)

# Strategy 2: Batch by KPI
for kpi in KPI_IDS:
    df_kpi = fetch_kolada_data([kpi], MUNICIPALITY_IDS, YEARS)
    # Process and save each KPI separately
    df_kpi.write.format("delta").mode("append").save(table_path)

# Strategy 3: Partition by municipality
BATCH_SIZE = 50
municipality_batches = [MUNICIPALITY_IDS[i:i+BATCH_SIZE] 
                       for i in range(0, len(MUNICIPALITY_IDS), BATCH_SIZE)]

for batch in municipality_batches:
    df_batch = fetch_kolada_data(KPI_IDS, batch, YEARS)
    df_batch.write.format("delta").mode("append").save(table_path)
```

## Scheduling Recommendations

Configure notebook schedules based on data update frequency:

- **KPI Metadata**: Monthly or quarterly (data changes infrequently)
- **Municipality Metadata**: Quarterly (rarely changes)
- **Data Ingestion**: 
  - Full refresh: Annually (after publication season)
  - Incremental: Monthly (for updates to existing data)
  - Real-time: Not needed (data published annually)

## Tips for Finding KPIs

After running notebook 01, query the metadata:

```python
# In a Fabric notebook or SQL endpoint
SELECT id, title, description
FROM kpi_metadata
WHERE title LIKE '%keyword%'
ORDER BY title;

# Common search keywords:
# - 'kostnad' (cost)
# - 'personal' (staff)
# - 'andel' (proportion)
# - 'antal' (number)
# - 'nöjd' (satisfied)
```

## Custom Table Names

To keep historical versions:

```python
# Modify table names to include version/date
table_path = f"Tables/kolada_data_{datetime.now().strftime('%Y%m')}"
df_data.write.format("delta").mode("overwrite").save(table_path)
```

## Error Recovery

For handling large ingestion failures:

```python
# Save checkpoint of successfully processed items
processed_items = []

for kpi in KPI_IDS:
    try:
        df = fetch_kolada_data([kpi], MUNICIPALITY_IDS, YEARS)
        df.write.format("delta").mode("append").save(table_path)
        processed_items.append(kpi)
    except Exception as e:
        print(f"Failed to process {kpi}: {e}")
        # Continue with next KPI

# Save checkpoint
with open('checkpoint.json', 'w') as f:
    json.dump({'processed': processed_items}, f)
```
