# Contributing to AWS Data Engineering Lakehouse Architecture

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. Check if the issue already exists in [GitHub Issues](https://github.com/Sairamyadav1/AWS-Data-Engineering-Lakehouse-Architecture/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (AWS region, Glue version, etc.)
   - Sample code or logs if applicable

### Suggesting Enhancements

For new features or improvements:

1. Open an issue describing the enhancement
2. Explain the use case and benefits
3. Provide examples if possible
4. Wait for feedback before implementing

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/Sairamyadav1/AWS-Data-Engineering-Lakehouse-Architecture.git
   cd AWS-Data-Engineering-Lakehouse-Architecture
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed
   - Add tests if applicable

4. **Test Your Changes**
   - Test locally before submitting
   - Ensure no existing functionality breaks
   - Verify all scripts run successfully

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of changes"
   ```
   
   Commit message format:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Link related issues

### Pull Request Guidelines

- **Title**: Clear and descriptive
- **Description**: Explain what and why
- **Testing**: Describe how you tested
- **Screenshots**: Include for UI changes
- **Documentation**: Update if needed

## Code Style

### Python (PySpark/Glue)

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Use type hints where appropriate

Example:
```python
def transform_data(df: DataFrame, column: str) -> DataFrame:
    """
    Transform data by applying business logic.
    
    Args:
        df: Input DataFrame
        column: Column name to transform
        
    Returns:
        Transformed DataFrame
    """
    return df.withColumn(f"{column}_transformed", col(column) * 2)
```

### SQL (Athena)

- Use uppercase for SQL keywords
- Use meaningful table/column aliases
- Add comments for complex queries
- Format for readability

Example:
```sql
-- Calculate monthly revenue by category
SELECT 
    year,
    month,
    category,
    SUM(amount) as total_revenue
FROM gold_db.transactions
WHERE year = 2024
GROUP BY year, month, category
ORDER BY total_revenue DESC;
```

### JSON Configuration

- Use 2-space indentation
- Keep keys sorted alphabetically (where order doesn't matter)
- Add comments in accompanying README files

### Documentation

- Use Markdown for all documentation
- Include code examples where helpful
- Keep language clear and concise
- Update table of contents when adding sections

## Areas for Contribution

### High Priority

- [ ] Additional data quality checks
- [ ] Performance optimization examples
- [ ] More complex ETL patterns
- [ ] Real-world use cases
- [ ] Cost optimization strategies
- [ ] Security hardening examples

### Documentation

- [ ] Video tutorials
- [ ] Step-by-step guides with screenshots
- [ ] FAQ section
- [ ] Troubleshooting scenarios
- [ ] Architecture decision records (ADRs)

### Code

- [ ] Unit tests for Glue scripts
- [ ] Integration test framework
- [ ] CI/CD pipeline examples
- [ ] Infrastructure as Code (Terraform/CloudFormation)
- [ ] Additional data source connectors
- [ ] Custom Glue transformations

### Examples

- [ ] E-commerce analytics pipeline
- [ ] IoT data processing
- [ ] Log analytics
- [ ] Real-time streaming integration
- [ ] Machine learning feature engineering

## Testing

### Local Testing

For Glue scripts:
```bash
# Set up local Glue environment
docker run -it -v ~/.aws:/root/.aws -v $(pwd):/home/glue_user/workspace/ \
  amazon/aws-glue-libs:glue_libs_4.0.0_image_01 \
  pyspark
```

### AWS Testing

- Test in a separate AWS account or dedicated test environment
- Use sample data (not production data)
- Clean up resources after testing
- Document any AWS costs incurred

## Review Process

1. **Automated Checks**: GitHub Actions will run linters and tests
2. **Code Review**: Maintainer will review the code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, PR will be merged
5. **Release**: Changes included in next release

## Community Guidelines

- Be respectful and constructive
- Welcome newcomers and help them get started
- Focus on the issue, not the person
- Give credit where due
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create an issue with details
- **Chat**: Join our community (if applicable)
- **Email**: Contact maintainer (if urgent)

## Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Given credit in commit messages

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to make this project better! 🎉
