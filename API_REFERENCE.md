# Kolada API Quick Reference

This document provides a quick reference for the Kolada API endpoints used in this project.

## Base URL

```
http://api.kolada.se/v2
```

## Common Parameters

- `per_page`: Number of results per page (max 5000, default 5000)
- `title`: Search filter for entity names
- `from_date`: Get changes since this date (format: YYYY-MM-DD)

## Metadata Endpoints

### KPIs (Key Performance Indicators)

```
GET /kpi
GET /kpi/{id}
GET /kpi?title={search_term}
```

**Response Structure:**
```json
{
  "values": [
    {
      "id": "N00945",
      "title": "KPI title",
      "description": "Description",
      "municipality_type": "K|L|A",
      "is_divided_by_gender": 0|1,
      "has_ou_data": true|false,
      "publication_date": "YYYY-MM-DD"
    }
  ],
  "count": 100,
  "next_page": "url_to_next_page"
}
```

### Municipalities

```
GET /municipality
GET /municipality/{id}
GET /municipality?title={search_term}
```

**Response Structure:**
```json
{
  "values": [
    {
      "id": "1860",
      "title": "Lund",
      "type": "K|L"
    }
  ]
}
```

Types:
- `K` = Kommun (Municipality)
- `L` = Landsting (County Council)

### Municipality Groups

```
GET /municipality_groups
GET /municipality_groups/{id}
```

**Response Structure:**
```json
{
  "values": [
    {
      "id": "group_id",
      "title": "Group name",
      "members": [
        {"id": "1860", "title": "Lund"}
      ]
    }
  ]
}
```

### KPI Groups

```
GET /kpi_groups
GET /kpi_groups/{id}
GET /kpi_groups?title={search_term}
```

**Response Structure:**
```json
{
  "values": [
    {
      "id": "group_id",
      "title": "Group name",
      "members": [
        {"id": "N00945", "title": "KPI title"}
      ]
    }
  ]
}
```

### Organizational Units

```
GET /ou
GET /ou/{id}
GET /ou?title={search_term}
GET /ou?municipality={municipality_id}&title={search_term}
```

**Response Structure:**
```json
{
  "values": [
    {
      "id": "V15E144001301",
      "municipality": "1860",
      "title": "School name"
    }
  ]
}
```

## Data Endpoints

### Municipality Data

```
GET /data/kpi/{kpi_id}/municipality/{municipality_id}/year/{year}
GET /data/kpi/{kpi_id}/year/{year}
GET /data/kpi/{kpi_id}/municipality/{municipality_id}
GET /data/municipality/{municipality_id}/year/{year}
```

**Parameters** (comma-separated for multiple values):
- `kpi_id`: One or more KPI IDs (e.g., `N00945,N00946`)
- `municipality_id`: One or more municipality IDs (e.g., `1860,0180`)
- `year`: One or more years (e.g., `2020,2021,2022`)

**Response Structure:**
```json
{
  "values": [
    {
      "kpi": "N00945",
      "municipality": "1860",
      "period": "2020",
      "values": [
        {
          "gender": "T|K|M",
          "value": 123.45,
          "count": 1,
          "status": ""
        }
      ]
    }
  ]
}
```

Gender codes:
- `T` = Total (all genders)
- `K` = Kvinnor (Women)
- `M` = Män (Men)

### Organizational Unit Data

```
GET /oudata/kpi/{kpi_id}/ou/{ou_id}/year/{year}
GET /oudata/kpi/{kpi_id}/year/{year}
GET /oudata/kpi/{kpi_id}/ou/{ou_id}
GET /oudata/ou/{ou_id}/year/{year}
```

**Response Structure:**
```json
{
  "values": [
    {
      "kpi": "N15033",
      "ou": "V15E144001301",
      "period": "2020",
      "values": [
        {
          "gender": "T",
          "value": 98.5,
          "count": 1,
          "status": ""
        }
      ]
    }
  ]
}
```

## Incremental Updates

Add `from_date` parameter to data queries:

```
GET /data/kpi/{kpi_id}/year/{year}?from_date=2023-01-01
```

Response includes `is_deleted` flag for each record:

```json
{
  "values": [
    {
      "kpi": "N00945",
      "municipality": "1860",
      "period": "2020",
      "is_deleted": true|false,
      "values": [...]
    }
  ]
}
```

## Example Queries

### Get all KPIs related to education

```
http://api.kolada.se/v2/kpi?title=skola
```

### Get specific KPI details

```
http://api.kolada.se/v2/kpi/N00945
```

### Get all municipalities in Stockholm county

```
http://api.kolada.se/v2/municipality?title=stockholm
```

### Get data for a specific KPI and municipality

```
http://api.kolada.se/v2/data/kpi/N00945/municipality/1860/year/2020,2021,2022
```

### Get all data for a municipality in a year

```
http://api.kolada.se/v2/data/municipality/1860/year/2020
```

### Get data for multiple KPIs across all municipalities

```
http://api.kolada.se/v2/data/kpi/N00945,N00946/year/2020
```

### Get organizational units in a specific municipality

```
http://api.kolada.se/v2/ou?municipality=1860
```

## Rate Limits and Best Practices

1. **No Authentication Required**: The API is public and free to use

2. **Be Respectful**: 
   - Add delays between requests (0.5-1 second recommended)
   - Don't hammer the API with rapid requests

3. **Pagination**:
   - Maximum 5000 results per page
   - Always check for `next_page` in the response
   - Follow pagination links to get all data

4. **Timeouts**:
   - Set appropriate timeouts (30+ seconds recommended)
   - Handle timeout errors gracefully

5. **Caching**:
   - Metadata changes infrequently - cache locally
   - Use `from_date` for incremental data updates

## Error Handling

Common HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Endpoint or resource doesn't exist
- `500 Internal Server Error`: API error (retry later)

## Data Freshness

- **Metadata**: Updated occasionally (check publication dates in KPI data)
- **Municipal Data**: Usually updated annually (spring/summer)
- **Publication Schedule**: Check `publication_date` and `prel_publication_date` in KPI metadata

## Resources

- **Full API Documentation**: https://github.com/Hypergene/kolada/wiki/API
- **Kolada Website**: http://www.kolada.se
- **Data Provider**: RKA (Rådet för främjande av kommunala analyser)
