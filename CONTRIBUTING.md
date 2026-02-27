# Contributing to Kolada Fabric

Thank you for your interest in contributing to the Kolada Fabric project! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion for improvement:

1. Check if the issue already exists in the [Issues](https://github.com/villezekeviking/Kolada_Fabric/issues) section
2. If not, create a new issue with:
   - Clear title describing the problem
   - Detailed description of the issue
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (Fabric version, Python version, etc.)

### Suggesting Enhancements

For feature requests:

1. Open an issue with the label "enhancement"
2. Describe the feature and its benefits
3. Provide examples of how it would be used
4. Consider implementation details if possible

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/villezekeviking/Kolada_Fabric.git
   cd Kolada_Fabric
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the existing code style
   - Update documentation as needed
   - Test your changes

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Provide a clear description of your changes

## Development Guidelines

### Code Style

#### Python
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused on a single task

#### Notebooks
- Add markdown cells to explain each step
- Include comments for complex logic
- Show sample outputs where helpful
- Keep cells organized and logical

### Documentation

When adding or modifying features:

1. Update the README.md if user-facing
2. Update API_REFERENCE.md if API usage changes
3. Add inline comments for complex code

### Testing

Before submitting a pull request:

1. Test your changes in a Fabric environment
2. Verify all notebooks run without errors
3. Validate JSON files are properly formatted
4. Test with different configurations

### Notebook Development

When modifying notebooks:

1. Test with sample data first
2. Ensure error handling is robust
3. Add progress indicators for long operations
4. Include data validation and summaries
5. Consider performance for large datasets

## Areas for Contribution

### High Priority

- **Error Handling**: Improve error messages and recovery
- **Performance**: Optimize for large datasets
- **Incremental Loading**: Implement `from_date` parameter usage
- **Monitoring**: Add logging and monitoring capabilities

### Medium Priority

- **Data Validation**: Add data quality checks
- **Scheduling**: Create templates for scheduled runs
- **Power BI Integration**: Add example reports
- **Configuration**: Expand configuration options

### Nice to Have

- **CI/CD**: Add GitHub Actions for testing
- **Examples**: Add example analyses and visualizations
- **Multiple Languages**: Support for other languages
- **Data Catalog**: Create metadata explorer
- **API Rate Limiting**: Smart retry logic

## Project Structure

```
Kolada_Fabric/
├── notebooks/              # Jupyter notebooks for data ingestion
├── config/               # Configuration files
├── docs/                 # Additional documentation (future)
├── tests/                # Unit tests (future)
├── examples/             # Example queries and reports (future)
└── README.md
```

## Coding Standards

### Naming Conventions

- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`

### File Naming

- **Notebooks**: `##_Description_With_Underscores.ipynb`
- **Python Scripts**: `descriptive_name.py`
- **Config Files**: `config.json`, `settings.json`

### Comments

```python
# Good: Explains why, not what
# Use retry logic because API can be unstable during peak hours
retry_count = 3

# Bad: States the obvious
# Set retry count to 3
retry_count = 3
```

### Function Documentation

```python
def fetch_data(kpi_ids: List[str], years: List[str]) -> pd.DataFrame:
    """
    Fetch Kolada data for specified KPIs and years.
    
    Args:
        kpi_ids: List of KPI identifiers to fetch
        years: List of years in YYYY format
        
    Returns:
        DataFrame containing the fetched data with columns:
        kpi, municipality, period, gender, value
        
    Raises:
        requests.RequestException: If API request fails
        ValueError: If parameters are invalid
    """
    pass
```

## Review Process

1. **Automated Checks**
   - Code syntax validation
   - JSON file validation
   - Style checking (future)

2. **Manual Review**
   - Code quality and style
   - Documentation completeness
   - Test coverage
   - Security considerations

3. **Testing**
   - Functional testing in Fabric
   - Edge case validation
   - Performance testing

## Security

- Never commit credentials or secrets
- Use environment variables for sensitive data
- Follow secure coding practices
- Report security issues privately

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Create an issue with details
- **Feature Ideas**: Start a discussion first
- **Documentation**: Check the docs folder

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors will be acknowledged in the project documentation and release notes.

Thank you for contributing to Kolada Fabric! 🎉
