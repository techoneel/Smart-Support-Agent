# Contributing to Smart Support Agent

Thank you for your interest in contributing to Smart Support Agent! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests to ensure everything works:
   ```bash
   python -m pytest
   ```
4. Update documentation if needed
5. Commit your changes with clear commit messages
6. Push to your fork and submit a pull request

## Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use type hints for function parameters and return values
- Write docstrings for classes and public methods
- Keep functions focused and single-purpose
- Add comments for complex logic

## Testing Requirements

- Maintain test coverage at or above 93%
- Write unit tests for new features
- Add integration tests for component interactions
- Include end-to-end tests for new channels
- Test both success and error cases

## Pull Request Process

1. Update the README.md with details of significant changes
2. Update ARCHITECTURE.md if you've modified the system design
3. Ensure all tests pass and code coverage meets requirements
4. Add yourself to the list of contributors (optional)
5. Request review from maintainers

## Best Practices

- Keep PRs focused and reasonably sized
- Rebase your branch on main before submitting
- Resolve conflicts before requesting review
- Respond to review comments promptly
- Update the documentation alongside code changes

## Getting Help

- Check existing issues and pull requests
- Use clear and descriptive titles for issues
- Provide reproduction steps for bugs
- Ask questions in issue discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
