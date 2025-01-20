"""
Module devoted to:
- create the necessary folder structure,
- generate a .env file from the .env.example template.
"""

from pathlib import Path
import shutil


def create_project_structure() -> None:
    """Create the initial project directory structure."""
    directories = [
        "src",
        "src/api/models",
        "src/api/routes",
        "src/config",
        "src/database",
        "tests/",
        "logs/",
    ]
    for directory in directories:
        # Create directories
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py in Python packages
        if not directory.startswith("logs"):
            init_file = Path(directory) / "__init__.py"
            init_file.touch(exist_ok=True)

    print("✅ Project structure created!")


def setup_environment_files() -> None:
    """Set up environment and configuration files."""
    # Create .env from example if it doesn't exist
    env_example = Path(".env.example")
    env_file = Path(".env")

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example!")

    # Create .gitkeep in logs directory (git doesn't track empty directories)
    (Path("logs") / ".gitkeep").touch(exist_ok=True)

    print("✅ Environment files set up!")


def main() -> None:
    """Run the project's full initialization."""
    print("⏳ Creating project structure...")
    create_project_structure()
    print("⏳ Setting environment files...")
    setup_environment_files()
    print("\nProject initialization completed! 🚀")


if __name__ == "__main__":
    main()
