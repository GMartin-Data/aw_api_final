"""
Main script to manage full setup:
- Project folder structure with running 'setup_project.py',
- ODBC install with running 'setup_odbc.sh'.
"""

import subprocess


def run_python_setup():
    """Run the setup_project.py script."""
    try:
        print("📁 Running setup_project.py...")
        subprocess.run(["python3", "setup_project.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running setup_project.py: {e}")
        exit(1)


def run_bash_setup():
    """Run the setup_odbc.sh script."""
    try:
        print("🛢️ Running setup_odbc.sh...")
        subprocess.run(["bash", "setup_odbc.sh"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running setup_odbc.sh: {e}")
        exit(1)


if __name__ == "__main__":
    print("⏳ Starting setup process...")
    run_python_setup()
    run_bash_setup()
    print("✅ Setup process completed successfully!")
