
import json
from pathlib import Path
from typing import Tuple
from .models import AppConfig
from .ui import Colors
import jsonschema

class ConfigLoader:
    """Loads configuration from file with validation and provides robust defaults."""
    CONFIG_FILES = [Path(".codexrc.json"), Path("codex.json")]

    APP_SETTINGS_SCHEMA = {
        "type": "object",
        "properties": {
            "max_workers": {"type": "number"},
            "history_file": {"type": "string"},
            "output_dir": {"type": "string"},
            "default_timeout": {"type": "number"},
            "skip_dirs": {"type": "array", "items": {"type": "string"}},
        },
        "additionalProperties": False,
    }

    TOOL_SCHEMA = {
        "type": "object",
        "properties": {
            "tool": {"type": "string"},
            "command": {"type": "array", "items": {"type": "string"}},
            "check": {"type": "boolean"},
            "fix": {"type": "boolean"},
            "timeout": {"type": "number"},
        },
        "required": ["tool", "command", "check", "fix"],
        "additionalProperties": False,
    }

    LANGUAGE_TOOLS_SCHEMA = {
        "type": "object",
        "patternProperties": {
            "^[a-zA-Z0-9/+-]+$": {
                "type": "array",
                "items": TOOL_SCHEMA,
            }
        },
        "additionalProperties": False,
    }

    # Hardcoded Safe Defaults
    DEFAULT_TOOL_MAP = {
        'python': [
            {'tool': 'pylint', 'command': ['pylint', '--output-format=json', '--score=n'], 'check': True, 'fix': False, 'timeout': 30},
            {'tool': 'black', 'command': ['black', '-q'], 'check': False, 'fix': True, 'timeout': 30}
        ],
        'javascript': [
            {'tool': 'eslint', 'command': ['eslint', '--format=json'], 'check': True, 'fix': False, 'timeout': 30},
            {'tool': 'prettier', 'command': ['prettier', '--write'], 'check': False, 'fix': True, 'timeout': 30}
        ]
    }

    @staticmethod
    def _validate_config(config_data: dict) -> None:
        """Validates the loaded configuration against the schemas."""
        if "app_settings" in config_data:
            try:
                jsonschema.validate(instance=config_data["app_settings"], schema=ConfigLoader.APP_SETTINGS_SCHEMA)
            except jsonschema.exceptions.ValidationError as e:
                print(f"{Colors.RED}[ERROR] Invalid 'app_settings' in config: {e.message}{Colors.RESET}")
        if "language_tools" in config_data:
            try:
                jsonschema.validate(instance=config_data["language_tools"], schema=ConfigLoader.LANGUAGE_TOOLS_SCHEMA)
            except jsonschema.exceptions.ValidationError as e:
                print(f"{Colors.RED}[ERROR] Invalid 'language_tools' in config: {e.message}{Colors.RESET}")


    @staticmethod
    def load() -> Tuple[AppConfig, dict]:
        config_data = {}

        for file_path in ConfigLoader.CONFIG_FILES:
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        loaded_json = json.load(f)
                        ConfigLoader._validate_config(loaded_json)
                        config_data.update(loaded_json)
                        print(f"{Colors.GREEN}[INFO] Loaded configuration from {file_path}.{Colors.RESET}")
                        break
                except json.JSONDecodeError as e:
                    print(f"{Colors.RED}[ERROR] Failed to decode {file_path}: {e}. Skipping.{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}[ERROR] Failed to load {file_path}: {e}. Skipping.{Colors.RESET}")

        app_settings = config_data.get('app_settings', {})
        tool_map = config_data.get('language_tools', ConfigLoader.DEFAULT_TOOL_MAP)

        config = AppConfig(
            max_workers=app_settings.get('max_workers', 4),
            history_file=app_settings.get('history_file', 'codex_history.json'),
            output_dir=app_settings.get('output_dir', 'reports'),
            default_timeout=app_settings.get('default_timeout', 30),
            skip_dirs=set(app_settings.get('skip_dirs', [])) | AppConfig.DEFAULT_SKIP
        )

        return config, tool_map
