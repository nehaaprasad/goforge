# Test package for goforge backend.
import os

# Avoid writing SQLite files during unit tests unless a test overrides this.
os.environ.setdefault("GOFORGE_PERSISTENCE_ENABLED", "false")
