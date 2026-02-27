# Example Configurations for Kolada Fabric

This file provides example configurations for different use cases with the unified fact table approach.

## Understanding the Star Schema

The data model uses Power BI star schema naming:
- **Dimensions** (prefix `d`): `dKpi`, `dMunicipality`, `dOrganizationalUnit`, `dMunicipalityGroup`, `dKpiGroup`
- **Facts** (prefix `f`): `fKoladaData` (unified fact table)
- **Bridge tables** (prefix `br`): `brMunicipalityGroupMember`, `brKpiGroupMember`

All dimensions have integer surrogate keys (`kpi_key`, `municipality_key`, `ou_key`) for optimal Power BI performance.

## Example 1: Basic Municipality Performance Dashboard

For analyzing general municipality performance across Sweden:

```python
# In notebook 03_Fetch_Kolada_Data.ipynb

# Municipality data parameters
KPI_IDS = [
    "N00945",  # Example KPI 1
    "N00946",  # Example KPI 2
    # Add more KPI IDs after running notebook 01 (check dKpi table)
]

# All municipalities (leave empty)
MUNICIPALITY_IDS = []

# Recent years
YEARS = ["2020", "2021", "2022", "2023"]

# OU data parameters (can be empty if not needed)
OU_KPI_IDS = []
OU_IDS = []
OU_YEARS = []
```

**Result:** Municipality-level data will have `ou_id` starting with "NO_OU_" in the unified `fKoladaData` table.

## Example 2: Specific Municipality Deep Dive

For detailed analysis of specific municipalities:

```python
# Focus on Stockholm, Göteborg, Malmö
MUNICIPALITY_IDS = ["0180", "1480", "1280"]

# Specific KPIs (filter by category after checking dKpi table)
KPI_IDS = ["N00945", "N00946", "N00947"]

YEARS = ["2018", "2019", "2020", "2021", "2022", "2023"]

# No OU data for this analysis
OU_KPI_IDS = []
OU_IDS = []
OU_YEARS = []
```

## Example 3: Education Sector Analysis with School-Level Data

For education-focused KPIs with both municipality and school (OU) level data:

```python
# Education KPIs (check dKpi table where has_ou_data = true)
KPI_IDS = [
    # Add education-related KPI IDs from notebook 01
    # Search for keywords: "skola", "elev", "utbildning"
]

# All municipalities
MUNICIPALITY_IDS = []

# Academic years
YEARS = ["2019", "2020", "2021", "2022", "2023"]

# OU data for school-level analysis
OU_KPI_IDS = [
    "N15033",  # Example: School KPI
    "N15030",  # Example: Another school KPI
]

# All schools (or filter by specific OUs from dOrganizationalUnit table)
OU_IDS = []

OU_YEARS = ["2019", "2020", "2021", "2022", "2023"]
```

**Result:** Unified `fKoladaData` table contains:
- Municipality-level education data (ou_id starts with "NO_OU_")
- School-level education data (ou_id is the actual school ID)
- Use `ou_key` to filter or join with `dOrganizationalUnit` dimension

## Example 4: Healthcare/Social Services

For healthcare and social services analysis:

```python
# Healthcare KPIs (check dKpi table)
KPI_IDS = [
    # Add healthcare-related KPI IDs from notebook 01
    # Search for keywords: "vård", "äldreomsorg", "hälsa"
]

# All municipalities
MUNICIPALITY_IDS = []

YEARS = ["2020", "2021", "2022", "2023"]

# OU data if analyzing specific care facilities
OU_KPI_IDS = []  # Add if needed
OU_IDS = []
OU_YEARS = []
```

## Example 5: Regional Comparison Using Municipality Groups

For comparing regions (using municipality groups):

1. First, run notebook 02 to get municipality groups
2. Query `dMunicipalityGroup` and `brMunicipalityGroupMember` tables to find groups of interest
3. Extract municipality IDs from the bridge table

```python
# In Power BI or a query notebook, find municipality IDs in a group:
# SELECT member_id FROM brMunicipalityGroupMember WHERE group_id = 'your_group_id'

KPI_IDS = ["N00945", "N00946"]

# Use municipality IDs from your selected group
MUNICIPALITY_IDS = ["0180", "1480", "1280"]  # Example: major cities

YEARS = ["2020", "2021", "2022"]

OU_KPI_IDS = []
OU_IDS = []
OU_YEARS = []
```

**Power BI Tip:** Use the `brMunicipalityGroupMember` bridge table to create many-to-many relationships between groups and the fact table.

## Example 6: Organizational Unit Deep Dive

For school or department level analysis:

```python
# First, query dOrganizationalUnit to find OUs of interest
# Filter by municipality if needed

# KPIs that have OU data (check has_ou_data = true in dKpi table)
OU_KPI_IDS = [
    "N15033",
    "N15030",
    # Add more OU-level KPIs
]

# Specific organizational units (from dOrganizationalUnit table)
# Or leave empty for all
OU_IDS = []

OU_YEARS = ["2020", "2021", "2022"]

# You can also include municipality-level KPIs for comparison
KPI_IDS = ["N00945"]  # Municipality-level equivalent
MUNICIPALITY_IDS = []
YEARS = ["2020", "2021", "2022"]
```

**Result:** The unified `fKoladaData` table allows you to compare municipality-level and OU-level data side-by-side.

**Power BI DAX Example:**
```dax
// Measure to show only municipality-level data
Municipality Level = 
CALCULATE(
    SUM(fKoladaData[value]),
    FILTER(fKoladaData, LEFT(fKoladaData[ou_id], 6) = "NO_OU_")
)

// Measure to show only OU-level data
OU Level = 
CALCULATE(
    SUM(fKoladaData[value]),
    FILTER(fKoladaData, LEFT(fKoladaData[ou_id], 6) <> "NO_OU_")
)
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
    "kpi": "dKpi",
    "municipality": "dMunicipality",
    "municipality_groups": "dMunicipalityGroup",
    "municipality_group_members": "brMunicipalityGroupMember",
    "kpi_groups": "dKpiGroup",
    "kpi_group_members": "brKpiGroupMember",
    "ou": "dOrganizationalUnit",
    "data": "fKoladaData"
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

After running notebook 01, query the dKpi dimension table:

```sql
-- In a Fabric notebook or SQL endpoint
SELECT id, title, description, has_ou_data
FROM dKpi
WHERE title LIKE '%keyword%'
ORDER BY title;

-- Common search keywords:
-- - 'kostnad' (cost)
-- - 'personal' (staff)
-- - 'andel' (proportion)
-- - 'antal' (number)
-- - 'nöjd' (satisfied)

-- Find KPIs with OU data available:
SELECT id, title
FROM dKpi
WHERE has_ou_data = 1
ORDER BY title;
```

## Power BI Relationship Setup

When creating your Power BI model, set up these relationships using surrogate keys:

1. **Fact to Dimensions (Many-to-One):**
   - `fKoladaData[kpi_key]` → `dKpi[kpi_key]`
   - `fKoladaData[municipality_key]` → `dMunicipality[municipality_key]`
   - `fKoladaData[ou_key]` → `dOrganizationalUnit[ou_key]`

2. **Bridge Tables (Many-to-Many via bridge):**
   - `dMunicipalityGroup[id]` → `brMunicipalityGroupMember[group_id]`
   - `brMunicipalityGroupMember[municipality_key]` → `dMunicipality[municipality_key]`
   - `dKpiGroup[id]` → `brKpiGroupMember[group_id]`
   - `brKpiGroupMember[kpi_id]` → `dKpi[id]` (business key)

3. **OU to Municipality (Many-to-One):**
   - `dOrganizationalUnit[municipality]` → `dMunicipality[id]` (business key)

**Important:** Always use surrogate keys (integer columns) for fact-to-dimension relationships for best performance.

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
