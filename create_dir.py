from pathlib import Path

# Root directory
root = Path("evalkit")

# Directories
directories = [
    root / "datasets",
    root / "scorers",
    root / "runners",
    root / "reporters",
    root / "ci",
]

# Files
files = [
    root / "__init__.py",
    root / "config.py",
    root / "types.py",
    root / "datasets" / "__init__.py",
    root / "scorers" / "__init__.py",
    root / "runners" / "__init__.py",
    root / "reporters" / "__init__.py",
    root / "ci" / "__init__.py",
]

# Create directories
for directory in directories:
    directory.mkdir(parents=True, exist_ok=True)

# Create files
for file in files:
    file.touch(exist_ok=True)

print("evalkit project structure created successfully!")

# Display structure
for path in sorted(root.rglob("*")):
    print(path)