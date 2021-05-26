import json
from pathlib import Path
from typing import Any, Mapping

import arrow


JsonMapping = Mapping[str, Any]


def load_schema(path: str, filename: str = "input_schema.json") -> JsonMapping:
    """
    Loads a schema at a given path. If the given path is a directory, the
    schema will be loaded from that directory. If the given path is a file,
    the schema will be loaded relative to the path's parent directory.
    """
    loc = Path(path)
    if loc.is_dir():
        schema_dir = loc
    else:
        schema_dir = loc.parent

    with (schema_dir / filename).open() as f:
        return json.load(f)


def iso_tz_now() -> str:
    """
    Returns an iso8601 compliant, timezone aware timestamp.
    """
    return str(arrow.utcnow())
