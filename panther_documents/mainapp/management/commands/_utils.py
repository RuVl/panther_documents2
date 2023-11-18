import json
from pathlib import Path
from typing import Union


JSON_PATH = Path('mainapp/management/jsons')


def load_from_json(file_name: Union[str, Path]) -> dict:
    with open(JSON_PATH / file_name, 'r', encoding='UTF-8') as f:
        return json.load(f)