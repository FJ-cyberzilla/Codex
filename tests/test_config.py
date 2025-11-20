
import os
import json
from pathlib import Path
from codex_enterprise.config import ConfigLoader
from codex_enterprise.models import AppConfig
import pytest

def test_load_default_config():
    """Tests that the default configuration is loaded correctly."""
    config, tool_map = ConfigLoader.load()
    assert isinstance(config, AppConfig)
    assert config.max_workers == 4
    assert config.history_file == "codex_history.json"
    assert config.output_dir == "reports"
    assert config.default_timeout == 30
    assert isinstance(tool_map, dict)
    assert "python" in tool_map
    assert "javascript" in tool_map

def test_load_custom_config(tmp_path: Path):
    """Tests that a custom configuration file is loaded correctly."""
    custom_config = {
        "app_settings": {
            "max_workers": 8,
            "history_file": "custom_history.json",
            "output_dir": "custom_reports",
            "default_timeout": 60,
            "skip_dirs": ["custom_skip"]
        },
        "language_tools": {
            "python": [
                {"tool": "flake8", "command": ["flake8"], "check": True, "fix": False}
            ]
        }
    }
    config_file = tmp_path / ".codexrc.json"
    with open(config_file, 'w') as f:
        json.dump(custom_config, f)

    # Change directory to the temporary path to ensure the config is found
    os.chdir(tmp_path)

    config, tool_map = ConfigLoader.load()
    assert isinstance(config, AppConfig)
    assert config.max_workers == 8
    assert config.history_file == "custom_history.json"
    assert config.output_dir == "custom_reports"
    assert config.default_timeout == 60
    assert "custom_skip" in config.skip_dirs
    assert "python" in tool_map
    assert tool_map["python"][0]["tool"] == "flake8"

    # Change back to the original directory
    os.chdir(Path(__file__).parent.parent)

def test_load_invalid_config(tmp_path: Path, capsys):
    """Tests that an invalid configuration file is handled correctly."""
    invalid_config = {
        "app_settings": {
            "max_workers": "not a number",
        },
        "language_tools": {
            "python": [
                {"tool": "flake8", "command": ["flake8"], "check": "not a boolean", "fix": False}
            ]
        }
    }
    config_file = tmp_path / ".codexrc.json"
    with open(config_file, 'w') as f:
        json.dump(invalid_config, f)

    os.chdir(tmp_path)

    ConfigLoader.load()
    captured = capsys.readouterr()
    assert "Invalid 'app_settings' in config" in captured.out
    assert "'not a number' is not of type 'number'" in captured.out
    assert "Invalid 'language_tools' in config" in captured.out
    assert "'not a boolean' is not of type 'boolean'" in captured.out
    os.chdir(Path(__file__).parent.parent)
