#!/usr/bin/env python3
"""Recursively read all secrets for the Vault K/V engine."""

import json
import os

def get_all_kv_secrets(path):
    """List all secrets in the given path from vault KV engine."""
    output = os.popen(f"vault kv list -format=json {path}").read()

    # If this is a leaf node, run 'vault kv get'
    if output.startswith("{"):
        data = os.popen(f"vault kv get -format=json {path}").read()
        print (data)

    # not a leaf node
    else:
        subdirs = json.loads(output)
        for subdir in subdirs:
            subdir_path = f"{path}/{subdir}"
            print(subdir_path)
            get_all_kv_secrets(subdir_path)

if __name__ == "__main__":
    get_all_kv_secrets("secrets/")
