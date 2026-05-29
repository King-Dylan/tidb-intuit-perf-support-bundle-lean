#!/usr/bin/env python3
"""
Shared DB config module — used by setup_schema.py, load_data.py, and demo.py.
Credentials are stored in .db_config.json (demo-only convenience — not for production).
"""

import os
import json
from getpass import getpass

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(MODULE_DIR) if os.path.basename(MODULE_DIR) == 'lib' else MODULE_DIR
CONFIG_FILE = os.path.join(PROJECT_ROOT, '.db_config.json')


def save_db_config(config):
    """Save DB config to file so subsequent scripts can reuse it"""
    saveable = {k: v for k, v in config.items() if k != 'autocommit'}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(saveable, f)


def load_db_config():
    """Load DB config from file if it exists"""
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        config['autocommit'] = True
        return config
    except Exception:
        return None


def get_db_config(save_msg="subsequent scripts"):
    """Load saved config or prompt user for connection details"""
    saved = load_db_config()
    if saved:
        host = saved.get('host', 'localhost')
        port = saved.get('port', 4000)
        user = saved.get('user', 'root')
        db = saved.get('database', 'intuit_risk')
        has_ssl = 'ssl' in saved
        print("┌─ TiDB Connection ────────────────────────────────────────────")
        print("│  Using saved credentials")
        print(f"│  Host: {host}:{port}  User: {user}  DB: {db}  SSL: {'✅' if has_ssl else '❌'}")
        print("└──────────────────────────────────────────────────────────────")
        print()
        return saved

    print("┌─ TiDB Connection Setup ──────────────────────────────────────")
    print("│  Press Enter to use the default value shown in [brackets].")
    print(f"│  Credentials will be saved for {save_msg}.")
    print("└──────────────────────────────────────────────────────────────\n")

    host = input("  Host [localhost]: ").strip() or 'localhost'
    port = int(input("  Port [4000]: ").strip() or '4000')
    user = input("  Username [root]: ").strip() or 'root'
    password = getpass("  Password []: ").strip()
    database = input("  Database [intuit_risk]: ").strip() or 'intuit_risk'
    ca_path = input("  CA certificate path (optional, press Enter to skip): ").strip()

    config = {
        'host': host, 'port': port, 'user': user,
        'password': password, 'database': database, 'autocommit': True
    }

    if ca_path and os.path.exists(ca_path):
        config['ssl'] = {'ca': ca_path}
        print(f"  ✅ SSL enabled with CA: {ca_path}")
    elif not ca_path:
        default_ca = os.path.join(PROJECT_ROOT, 'ca.pem')
        default_ca2 = os.path.expanduser('~/Downloads/ca.pem')
        if os.path.exists(default_ca):
            config['ssl'] = {'ca': default_ca}
            print(f"  ✅ SSL enabled with CA: {default_ca}")
        elif os.path.exists(default_ca2):
            config['ssl'] = {'ca': default_ca2}
            print(f"  ✅ SSL enabled with CA: {default_ca2}")
        else:
            print("  ⚠️  No CA cert — connecting without SSL")
    else:
        print(f"  ⚠️  CA file not found at {ca_path} — connecting without SSL")

    print()
    save_db_config(config)
    print(f"  💾 Credentials saved for {save_msg}.\n")
    return config
