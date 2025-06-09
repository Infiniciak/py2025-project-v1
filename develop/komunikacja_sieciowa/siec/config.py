import yaml
from typing import Dict, Any
import logging



def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        required = ['host', 'port']
        for field in required:
            if field not in config.get('network', {}):
                raise ValueError(f"Missing required config field: {field}")

        return config['network']
    except Exception as e:
        logging.getLogger(__name__).error(f"Config loading error: {str(e)}")
        raise


def get_client_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    config = load_config(config_path)
    return {
        'host': config['host'],
        'port': config['port'],
        'timeout': config.get('timeout', 5.0),
        'retries': config.get('retries', 3)
    }


def get_server_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    config = load_config(config_path)
    return {
        'port': config['port']
    }