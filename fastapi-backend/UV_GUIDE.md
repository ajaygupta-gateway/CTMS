# Using UV Package Manager

This project uses [uv](https://github.com/astral-sh/uv) - a fast Python package installer and resolver written in Rust.

## Why UV?

- ⚡ **10-100x faster** than pip
- 🔒 **Reliable**: Consistent dependency resolution
- 🎯 **Simple**: Drop-in replacement for pip
- 🚀 **Modern**: Built for modern Python workflows

## Installation

UV is automatically installed by the `setup.sh` script. To install manually:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on macOS:
```bash
brew install uv
```

## Common Commands

### Creating Virtual Environment

```bash
# Create a new virtual environment
uv venv

# Create with specific Python version
uv venv --python 3.11
```

### Installing Packages

```bash
# Install from pyproject.toml
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Install a specific package
uv pip install fastapi

# Install from requirements.txt (legacy)
uv pip install -r requirements.txt
```

### Managing Dependencies

```bash
# Add a new dependency
# 1. Edit pyproject.toml and add to dependencies list
# 2. Run:
uv pip install -e ".[dev]"

# Sync dependencies (install/uninstall to match pyproject.toml)
uv pip sync

# Compile dependencies to requirements.txt
uv pip compile pyproject.toml -o requirements.txt
```

### Upgrading Packages

```bash
# Upgrade a specific package
uv pip install --upgrade package-name

# Upgrade all packages
uv pip install --upgrade -e ".[dev]"
```

### Other Useful Commands

```bash
# List installed packages
uv pip list

# Show package info
uv pip show package-name

# Uninstall a package
uv pip uninstall package-name

# Freeze dependencies
uv pip freeze
```

## Project Setup with UV

### First Time Setup

```bash
# 1. Clone the repository
cd fastapi-backend

# 2. Run setup script (installs uv automatically)
chmod +x setup.sh
./setup.sh

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Verify installation
python --version
uv --version
```

### Daily Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the application
python run.py

# Run tests
pytest

# Deactivate when done
deactivate
```

## pyproject.toml vs requirements.txt

This project uses `pyproject.toml` (modern Python standard) instead of `requirements.txt`:

### pyproject.toml (Recommended)
```toml
[project]
dependencies = [
    "fastapi==0.109.0",
    "uvicorn[standard]==0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest==7.4.4",
    "black==23.12.1",
]
```

**Advantages**:
- ✅ Standard Python packaging format
- ✅ Separates dev and prod dependencies
- ✅ Better for modern Python projects
- ✅ Includes project metadata

### requirements.txt (Legacy)
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
```

**When to use**:
- Legacy projects
- Simple scripts
- CI/CD that doesn't support pyproject.toml

## Migrating from pip to uv

If you're used to pip, here's the mapping:

| pip command | uv command |
|-------------|------------|
| `pip install package` | `uv pip install package` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip install -e .` | `uv pip install -e .` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |
| `pip uninstall package` | `uv pip uninstall package` |

**Note**: Just add `uv` before `pip` in most cases!

## Troubleshooting

### UV not found after installation

```bash
# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or reload shell
source ~/.bashrc  # or ~/.zshrc
```

### Virtual environment issues

```bash
# Remove and recreate
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Dependency conflicts

```bash
# Clear cache
uv cache clean

# Reinstall
rm -rf .venv
uv venv
uv pip install -e ".[dev]"
```

## Performance Comparison

Benchmark installing all project dependencies:

| Tool | Time |
|------|------|
| pip | ~45 seconds |
| uv | ~3 seconds |

**uv is 15x faster!** ⚡

## CI/CD Integration

### GitHub Actions

```yaml
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: |
    uv venv
    source .venv/bin/activate
    uv pip install -e ".[dev]"
```

### Docker

```dockerfile
# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install dependencies
RUN uv pip install -e .
```

## Resources

- **Official Docs**: https://github.com/astral-sh/uv
- **Installation**: https://astral.sh/uv/install
- **PyPI**: https://pypi.org/project/uv/

## Summary

UV makes Python package management:
- ⚡ **Faster**: 10-100x speed improvement
- 🔒 **Reliable**: Better dependency resolution
- 🎯 **Simple**: Drop-in pip replacement
- 🚀 **Modern**: Built for modern Python

Just remember: `uv pip install` instead of `pip install`!
