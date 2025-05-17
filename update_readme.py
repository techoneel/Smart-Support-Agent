#!/usr/bin/env python
"""Update README.md and ARCHITECTURE.md to reflect the new project structure."""

import re

def update_readme():
    """Update README.md with the new project structure."""
    print("Updating README.md...")
    
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Update CLI commands
        content = re.sub(
            r'python cli/main\.py',
            r'python -m smart_support_agent.cli.main',
            content
        )
        
        # Update project structure description
        if "## Project Structure" not in content:
            # Add project structure section if it doesn't exist
            structure_section = """
## Project Structure

The Smart Support Agent follows a modern Python package structure:

```
Smart-Support-Agent/
├── src/
│   └── smart_support_agent/  # Main package
│       ├── cli/              # Command-line interface
│       ├── config/           # Configuration handling
│       ├── core/             # Core business logic
│       │   ├── agents/       # Agent implementations
│       │   ├── ingestor/     # Document ingestion
│       │   ├── llm/          # LLM integration
│       │   └── retriever/    # Vector search
│       └── factory/          # Factory patterns
├── tests/                    # Test suite
├── setup.py                  # Package configuration
└── ...
```

This structure follows Python best practices and makes the package installable via pip.
"""
            # Find a good place to insert the structure section
            if "## Architecture" in content:
                content = content.replace("## Architecture", f"{structure_section}\n## Architecture")
            else:
                content += f"\n{structure_section}"
        
        # Update installation instructions
        content = re.sub(
            r'pip install -r requirements\.txt',
            r'pip install -e .',
            content
        )
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
            
        print("README.md updated successfully!")
        
    except Exception as e:
        print(f"Error updating README.md: {str(e)}")

def update_architecture():
    """Update ARCHITECTURE.md with the new project structure."""
    print("Updating ARCHITECTURE.md...")
    
    try:
        if not os.path.exists("ARCHITECTURE.md"):
            print("ARCHITECTURE.md not found, skipping...")
            return
            
        with open("ARCHITECTURE.md", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Update import paths
        content = re.sub(
            r'from (cli|config|core|factory)',
            r'from smart_support_agent.\1',
            content
        )
        
        # Update directory structure
        content = re.sub(
            r'Smart-Support-Agent/\n├── (cli|config|core|factory)/',
            r'Smart-Support-Agent/\n├── src/\n│   └── smart_support_agent/\n│       ├── \1/',
            content
        )
        
        with open("ARCHITECTURE.md", "w", encoding="utf-8") as f:
            f.write(content)
            
        print("ARCHITECTURE.md updated successfully!")
        
    except Exception as e:
        print(f"Error updating ARCHITECTURE.md: {str(e)}")

if __name__ == "__main__":
    import os
    update_readme()
    update_architecture()
    print("Documentation updates complete!")