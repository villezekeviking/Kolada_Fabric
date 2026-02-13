# Kolada Data Ingestion for Microsoft Fabric

This repository contains the resources needed to ingest, store, and analyze Kolada data in Microsoft Fabric and Power BI.

## Overview

[Kolada](http://www.kolada.se) provides a web service for accessing standardized Key Performance Indicators (KPIs) for Swedish municipalities and organizational units. This project provides automated scripts to:

- Fetch metadata (KPIs, municipalities, organizational units)
- Ingest data from the Kolada API into Microsoft Fabric Lakehouse
- Deploy all resources to a Fabric workspace automatically

## Project Structure

```
Kolada_Fabric/
├── notebooks/              # Fabric notebooks for data ingestion
│   ├── 01_Fetch_KPI_Metadata.ipynb
│   ├── 02_Fetch_Municipality_Metadata.ipynb
│   └── 03_Fetch_Kolada_Data.ipynb
├── deployment/            # Deployment automation scripts
│   └── deploy_to_fabric.py
├── config/               # Configuration files
│   └── config.json
└── README.md
```

## Features

- **Automated Metadata Ingestion**: Fetch all KPIs, municipalities, groups, and organizational units
- **Flexible Data Ingestion**: Configure which KPIs, municipalities, and years to fetch
- **Pagination Support**: Handles large datasets with automatic pagination
- **Delta Lake Storage**: Stores data in Delta format for optimal performance
- **Automated Deployment**: Deploy all resources to Fabric with a single script

## Prerequisites

1. **Microsoft Fabric Access**
   - Access to a Microsoft Fabric workspace
   - Permissions to create Lakehouses and Notebooks

2. **For Automated Deployment** (Optional):
   - Azure AD App Registration with Fabric API permissions
   - Service Principal credentials (Client ID, Client Secret, Tenant ID)

## Quick Start

### Option 1: Manual Setup (Recommended for First-Time Users)

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
   - **03_Fetch_Kolada_Data.ipynb**: Fetches actual data values

### Option 2: Automated Deployment

1. **Set Up Service Principal**
   ```bash
   # Set environment variables
   export FABRIC_TENANT_ID="your-tenant-id"
   export FABRIC_CLIENT_ID="your-client-id"
   export FABRIC_CLIENT_SECRET="your-client-secret"
   export FABRIC_WORKSPACE_NAME="KoladaWorkspace"  # Optional
   ```

2. **Install Dependencies**
   ```bash
   pip install requests
   ```

3. **Run Deployment Script**
   ```bash
   python deployment/deploy_to_fabric.py
   ```

   This will:
   - Create or update the Fabric workspace
   - Create a Lakehouse
   - Upload all notebooks
   - Configure the resources

## Configuration

Edit `config/config.json` to customize:

```json
{
  "api_base_url": "http://api.kolada.se/v2",
  "lakehouse_name": "KoladaLakehouse",
  "workspace_name": "KoladaWorkspace",
  "tables": {
    "kpi": "kpi_metadata",
    "municipality": "municipality_metadata",
    "data": "kolada_data"
  }
}
```

## Notebooks Description

### 01_Fetch_KPI_Metadata.ipynb

Fetches all KPI (Key Performance Indicator) metadata from Kolada API.

**Output Tables:**
- `kpi_metadata`: Contains all KPI definitions, descriptions, and metadata

**Key Features:**
- Automatic pagination handling
- Adds ingestion timestamp for tracking
- Summary statistics by municipality type and gender division

### 02_Fetch_Municipality_Metadata.ipynb

Fetches municipality, municipality groups, organizational units, and KPI groups metadata.

**Output Tables:**
- `municipality_metadata`: All Swedish municipalities and county councils
- `municipality_groups_metadata`: Municipality groupings
- `municipality_group_members`: Detailed membership information
- `kpi_groups_metadata`: KPI groupings
- `kpi_group_members`: KPI group membership details
- `organizational_units_metadata`: Organizational units (schools, departments, etc.)

**Key Features:**
- Flattens nested group structures
- Creates separate tables for group memberships
- Comprehensive metadata coverage

### 03_Fetch_Kolada_Data.ipynb

Fetches actual data values for specified KPIs, municipalities, and years.

**Customizable Parameters:**
```python
KPI_IDS = ["N00945", "N00946"]  # List of KPI IDs to fetch
MUNICIPALITY_IDS = []  # Empty for all, or specify IDs
YEARS = ["2020", "2021", "2022", "2023"]  # Years to fetch
```

**Output Tables:**
- `kolada_data`: Municipality-level data
- `kolada_ou_data`: Organizational unit-level data (optional)

**Key Features:**
- Flexible parameter configuration
- Handles gender-disaggregated data
- Data quality statistics
- Support for both municipality and OU data

## Data Schema

### KPI Metadata
```
id, title, description, definition, municipality_type, 
is_divided_by_gender, operating_area, has_ou_data, 
publication_date, ingestion_timestamp, source_system
```

### Municipality Metadata
```
id, title, type, ingestion_timestamp, source_system
```

### Kolada Data
```
kpi, municipality, period, gender, value, count, status,
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

### Issue: Deployment script fails
**Solution**: Verify your Service Principal has the correct permissions:
- `Workspace.ReadWrite.All` for Fabric workspaces
- Proper role assignments in Azure AD

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
