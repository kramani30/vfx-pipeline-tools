# VFX Pipeline Tools

A collection of Python pipeline utilities for VFX production, built to the standards used at major studios like ILM and Barnstorm VFX.

## Tools

### Asset Validator
Validates VFX assets before they are published to production. Checks:
- Naming convention (e.g. `char_hero_rig_v001`)
- File extension (Maya, Alembic, USD, FBX, OBJ)
- File existence on disk
- Version number validity
- Required metadata keys

## Usage

```python
from asset_validator import AssetValidator

validator = AssetValidator()
report = validator.validate(
    asset_name="char_hero_rig_v001",
    asset_path="/path/to/char_hero_rig_v001.mb",
    metadata={
        "asset_type": "char",
        "department": "rigging",
        "version": "001",
        "artist": "kramani"
    }
)
print(report.summary())
```

## Running Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Tech Stack

- Python 3.11+
- pytest — unit testing
- GitHub Actions — CI/CD on every push
