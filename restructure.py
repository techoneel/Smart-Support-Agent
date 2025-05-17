# restructure.py
import os
import shutil
import re
import sys

def restructure_project():
    print("Restructuring project to use src directory...")
    
    # Create directory structure
    os.makedirs("src/smart_support_agent", exist_ok=True)
    for dir_name in ["cli", "config", "core", "factory"]:
        os.makedirs(f"src/smart_support_agent/{dir_name}", exist_ok=True)
        # Create __init__.py files in subdirectories
        with open(f"src/smart_support_agent/{dir_name}/__init__.py", "w") as f:
            f.write(f'"""Smart Support Agent {dir_name} package."""\n')

    # Create main __init__.py file
    with open("src/smart_support_agent/__init__.py", "w") as f:
        f.write('"""Smart Support Agent package."""\n')

    # Move files
    for dir_name in ["cli", "config", "core", "factory"]:
        if os.path.exists(dir_name):
            print(f"Processing {dir_name}...")
            for item in os.listdir(dir_name):
                src_path = os.path.join(dir_name, item)
                dst_path = os.path.join(f"src/smart_support_agent/{dir_name}", item)
                if os.path.isfile(src_path):
                    print(f"  Copying {src_path} to {dst_path}")
                    shutil.copy2(src_path, dst_path)
                    
                    # Update imports in the file
                    if src_path.endswith('.py'):
                        try:
                            with open(dst_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Update relative imports
                            content = re.sub(r'from \.\.([\w]+)', r'from smart_support_agent.\1', content)
                            content = re.sub(r'from \.([\w]+)', r'from smart_support_agent.\1', content)
                            
                            # Update absolute imports
                            content = re.sub(r'from (cli|config|core|factory)', r'from smart_support_agent.\1', content)
                            content = re.sub(r'import (cli|config|core|factory)', r'import smart_support_agent.\1', content)
                            
                            with open(dst_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        except Exception as e:
                            print(f"    Error updating imports in {dst_path}: {str(e)}")
                elif os.path.isdir(src_path):
                    if not os.path.exists(dst_path):
                        os.makedirs(dst_path)
                    for subitem in os.listdir(src_path):
                        src_subpath = os.path.join(src_path, subitem)
                        dst_subpath = os.path.join(dst_path, subitem)
                        if os.path.isfile(src_subpath):
                            print(f"  Copying {src_subpath} to {dst_subpath}")
                            shutil.copy2(src_subpath, dst_subpath)
                            
                            # Update imports in the file
                            if src_subpath.endswith('.py'):
                                try:
                                    with open(dst_subpath, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    
                                    # Update relative imports
                                    content = re.sub(r'from \.\.([\w]+)', r'from smart_support_agent.\1', content)
                                    content = re.sub(r'from \.([\w]+)', r'from smart_support_agent.\1', content)
                                    
                                    # Update absolute imports
                                    content = re.sub(r'from (cli|config|core|factory)', r'from smart_support_agent.\1', content)
                                    content = re.sub(r'import (cli|config|core|factory)', r'import smart_support_agent.\1', content)
                                    
                                    with open(dst_subpath, 'w', encoding='utf-8') as f:
                                        f.write(content)
                                except Exception as e:
                                    print(f"    Error updating imports in {dst_subpath}: {str(e)}")

    # Update setup.py
    print("Updating setup.py...")
    try:
        with open("setup.py", "r", encoding='utf-8') as f:
            setup_content = f.read()

        setup_content = setup_content.replace(
            'packages=find_packages(include=["core*", "cli*", "config*", "factory*"])',
            'packages=find_packages(where="src")',
        )
        setup_content = setup_content.replace(
            'setup(',
            'setup(\n    package_dir={"": "src"},'
        )

        with open("setup.py", "w", encoding='utf-8') as f:
            f.write(setup_content)
    except Exception as e:
        print(f"Error updating setup.py: {str(e)}")
        
    # Create a simple CLI entry point script
    print("Creating CLI entry point...")
    try:
        with open("smart_support_agent.py", "w", encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python
from src.smart_support_agent.cli.main import cli

if __name__ == "__main__":
    cli()
""")

        # Make the script executable on Unix-like systems
        if sys.platform != "win32":
            os.chmod("smart_support_agent.py", 0o755)
    except Exception as e:
        print(f"Error creating CLI entry point: {str(e)}")

    # Update tests to use the new import structure
    print("Updating test imports...")
    if os.path.exists("tests"):
        for root, _, files in os.walk("tests"):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Update imports
                        content = re.sub(r'from (cli|config|core|factory)', r'from src.smart_support_agent.\1', content)
                        content = re.sub(r'import (cli|config|core|factory)', r'import src.smart_support_agent.\1', content)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                    except Exception as e:
                        print(f"    Error updating imports in {file_path}: {str(e)}")

    print("\nProject restructured successfully!")
    print("\nNext steps:")
    print("1. Review the changes and update any remaining imports manually")
    print("2. Update the README.md and ARCHITECTURE.md files (run update_readme.py)")
    print("3. Run tests to ensure everything works correctly")
    print("4. Use 'python -m src.smart_support_agent.cli.main' to run the CLI")
    print("   or 'python smart_support_agent.py'")

if __name__ == "__main__":
    restructure_project()