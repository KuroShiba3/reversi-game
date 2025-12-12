from alembic import command
from alembic.config import Config
from pathlib import Path

def run_migrations():
    root_dir = Path(__file__).parent.parent.parent
    alembic_ini_path = root_dir / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini_path))

    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise