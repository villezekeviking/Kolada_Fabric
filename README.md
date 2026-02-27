# Kolada Data Ingestion for Microsoft Fabric

This repository contains the resources needed to ingest, store, and analyze Kolada data in Microsoft Fabric and Power BI.

## Overview

[Kolada](http://www.kolada.se) provides a web service for accessing standardized Key Performance Indicators (KPIs) for Swedish municipalities and organizational units. This project provides automated scripts to:

- Fetch metadata (KPIs, municipalities, organizational units)
- Ingest data from the Kolada API into Microsoft Fabric Lakehouse

## Project Structure

```
Kolada_Fabric/
├── notebooks/              # Fabric notebooks for data ingestion
│   ├── 01_Fetch_KPI_Metadata.ipynb
│   ├── 02_Fetch_Municipality_Metadata.ipynb
│   └── 03_Fetch_Kolada_Data.ipynb
├── config/               # Configuration files
│   └── config.json
└── README.md
```

## Features

- **Power BI Star Schema**: Tables follow Power BI naming conventions (dimensions: `d*`, facts: `f*`, bridge: `br*`)
- **Surrogate Keys**: Integer surrogate keys on all dimensions for optimal Power BI performance
- **Unified Fact Table**: Single `fKoladaData` table combines municipality-level and OU-level data
- **Automated Metadata Ingestion**: Fetch all KPIs, municipalities, groups, and organizational units
- **Flexible Data Ingestion**: Configure which KPIs, municipalities, and years to fetch
- **Pagination Support**: Handles large datasets with automatic pagination
- **Delta Lake Storage**: Stores data in Delta format for optimal performance

## Prerequisites

**Microsoft Fabric Access**
- Access to a Microsoft Fabric workspace
- Permissions to create Lakehouses and Notebooks

## Quick Start

1. **Create a Workspace and Lakehouse in Fabric**
   - Log into Microsoft Fabric
   - Create a new Workspace (e.g., "KoladaWorkspace")
   - Create a Lakehouse (e.g., "KoladaLakehouse")

2. **Upload Notebooks**
   - Download or clone this repository
   - Upload the notebooks from the `notebooks/` folder to your Fabric workspace
   - Attach the Lakehouse to each notebook

3. **Run the Notebooks in Order**
   - **01_Fetch_KPI_Metadata.ipynb**: Fetches all KPI metadata
   - **02_Fetch_Municipality_Metadata.ipynb**: Fetches municipality and group metadata
   - **03_Fetch_Kolada_Data.ipynb**: Fetches actual data values (may need to run multiple times to get all the data)

## Configuration

Edit `config/config.json` to customize:

```json
{
  "api_base_url": "http://api.kolada.se/v2",
  "lakehouse_name": "KoladaLakehouse",
  "workspace_name": "KoladaWorkspace",
  "tables": {
    "kpi": "dKpi",
    "municipality": "dMunicipality",
    "municipality_groups": "dMunicipalityGroup",
    "municipality_group_members": "brMunicipalityGroupMember",
    "kpi_groups": "dKpiGroup",
    "kpi_group_members": "brKpiGroupMember",
    "ou": "dOrganizationalUnit",
    "data": "fKoladaData"
  }
}
```

## Notebooks Description

### 01_Fetch_KPI_Metadata.ipynb

Fetches all KPI (Key Performance Indicator) metadata from Kolada API.

**Output Tables:**
- `dKpi`: KPI dimension table with all KPI definitions, descriptions, and metadata
  - Includes `kpi_key` surrogate integer key for relationships
  - Business key: `id` column

**Key Features:**
- Automatic pagination handling
- Adds ingestion timestamp for tracking
- Integer surrogate key for Power BI relationships
- Summary statistics by municipality type and gender division

### 02_Fetch_Municipality_Metadata.ipynb

Fetches municipality, municipality groups, organizational units, and KPI groups metadata.

**Output Tables (Star Schema):**
- `dMunicipality`: Municipality dimension - All Swedish municipalities and county councils
  - Includes `municipality_key` surrogate integer key
  - Business key: `id` column
- `dMunicipalityGroup`: Municipality groupings
- `brMunicipalityGroupMember`: Bridge table for municipality group membership
  - Includes `municipality_key` surrogate key lookups
- `dKpiGroup`: KPI groupings
- `brKpiGroupMember`: Bridge table for KPI group membership
- `dOrganizationalUnit`: Organizational units (schools, departments, etc.)
  - Includes `ou_key` surrogate integer key
  - Business key: `id` column
  - Includes "No OU" placeholder rows for municipality-level data (id = "NO_OU_{municipality_id}")

**Key Features:**
- Power BI star schema naming (d*, br* prefixes)
- Integer surrogate keys on all dimensions
- "No OU" placeholders enable unified fact table
- Flattens nested group structures
- Creates separate bridge tables for many-to-many relationships
- Comprehensive metadata coverage

### 03_Fetch_Kolada_Data.ipynb

Fetches actual data values for specified KPIs, municipalities, and years. Creates a **unified fact table** that combines both municipality-level and OU-level data.

**Customizable Parameters:**
```python
# Municipality data
KPI_IDS = ["N00945", "N00946"]  # List of KPI IDs to fetch
MUNICIPALITY_IDS = []  # Empty for all, or specify IDs
YEARS = ["2020", "2021", "2022", "2023"]  # Years to fetch

# OU data (enabled by default)
OU_KPI_IDS = ["N15033", "N15030"]  # KPIs with OU data
OU_IDS = []  # Empty for all, or specify OU IDs
OU_YEARS = ["2020", "2021", "2022"]  # Years for OU data
```

**Output Table:**
- `fKoladaData`: Unified fact table containing both municipality-level and OU-level data
  - Municipality records: `ou_id` = "NO_OU_{municipality_id}"
  - OU records: `ou_id` = actual OU ID
  - Includes surrogate keys: `kpi_key`, `municipality_key`, `ou_key`
  - Business keys retained: `kpi`, `municipality`, `ou_id`

**Key Features:**
- Unified fact table approach (single source of truth)
- OU data ingestion enabled by default
- "No OU" placeholders for municipality-level data
- Integer surrogate keys for optimal Power BI performance
- Flexible parameter configuration
- Handles gender-disaggregated data
- Comprehensive data quality statistics
- Automatic municipality lookup for OU data

## Data Schema (Star Schema)

### Dimensions

#### dKpi (KPI Dimension)
```
kpi_key (surrogate key), id (business key), title, description, 
definition, municipality_type, is_divided_by_gender, operating_area, 
has_ou_data, publication_date, ingestion_timestamp, source_system
```

#### dMunicipality (Municipality Dimension)
```
municipality_key (surrogate key), id (business key), title, type, 
ingestion_timestamp, source_system
```

#### dOrganizationalUnit (OU Dimension)
```
ou_key (surrogate key), id (business key), municipality, title, 
ingestion_timestamp, source_system

Note: Includes "No OU" placeholder rows with id = "NO_OU_{municipality_id}"
```

### Fact Table

#### fKoladaData (Unified Fact)
```
kpi_key (FK), municipality_key (FK), ou_key (FK), 
kpi (business key), municipality (business key), ou_id (business key),
period, gender, value, count, status, 
ingestion_timestamp, source_system

Municipality-level data: ou_id starts with "NO_OU_"
OU-level data: ou_id is the actual organizational unit ID
```

### Bridge Tables

#### brMunicipalityGroupMember
```
group_id, group_title, member_id, member_title, municipality_key,
ingestion_timestamp, source_system
```

#### brKpiGroupMember
```
group_id, group_title, kpi_id, kpi_title,
ingestion_timestamp, source_system
```

## API Information

The Kolada API is:
- **Public and free** - No authentication required
- **RESTful JSON API** - Returns data in JSON format
- **Rate-limited** - Use delays between requests to be respectful
- **Paginated** - Max 5000 items per page

**API Documentation**: [Kolada API Wiki](https://github.com/Hypergene/kolada/wiki/API)

## Best Practices

1. **Start with Metadata**: Always run notebooks 01 and 02 before fetching data
2. **Test with Small Datasets**: Start with 1-2 KPIs before scaling up
3. **Use Incremental Loads**: Consider using the `from_date` parameter for updates
4. **Monitor API Usage**: Be respectful of API rate limits
5. **Validate Data**: Check summary statistics after each load

## Troubleshooting

### Issue: Cannot write to Lakehouse
**Solution**: Ensure the Lakehouse is properly attached to the notebook. The notebooks will fallback to saving Parquet files to the Files section.

### Issue: No data returned from API
**Solution**: 
- Check the KPI IDs are valid (use notebook 01 to see available KPIs)
- Verify the years have data (some KPIs only have recent years)
- Check your internet connectivity

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source. The Kolada data is provided by RKA and is publicly available.

## Resources

- [Kolada Website](http://www.kolada.se)
- [Kolada API Documentation](https://github.com/Hypergene/kolada/wiki/API)
- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)
- [Delta Lake Documentation](https://delta.io/)
