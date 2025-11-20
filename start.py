#!/usr/bin/env python3
"""
Start script for Railway deployment
Reads PORT from environment and starts gunicorn using config file
"""
import os
import sys

# DEBUG: Log all environment variables related to PORT
print("=" * 50)
print("DEBUG: Environment Variables")
print("=" * 50)
for key, value in sorted(os.environ.items()):
    if 'PORT' in key.upper():
        print(f"{key} = {value} (type: {type(value).__name__})")
print("=" * 50)

# Get PORT from environment or use default
port_raw = os.environ.get('PORT', '5000')
print(f"DEBUG: PORT raw value: '{port_raw}' (type: {type(port_raw).__name__})")

# Validate port is a number
try:
    port_int = int(port_raw)
    print(f"DEBUG: PORT converted to int: {port_int}")
    if port_int < 1 or port_int > 65535:
        print(f"ERROR: PORT must be between 1 and 65535, got {port_int}")
        sys.exit(1)
except ValueError as e:
    print(f"ERROR: PORT must be a number, got '{port_raw}'")
    print(f"ERROR: ValueError: {e}")
    print(f"ERROR: PORT value repr: {repr(port_raw)}")
    sys.exit(1)

# Use gunicorn with config file
# Config file will read PORT from environment again, but we've validated it here
gunicorn_args = [
    'gunicorn',
    '-c', 'gunicorn.conf.py',
    'app:app'
]

print(f"DEBUG: Gunicorn command: {' '.join(gunicorn_args)}")
print("=" * 50)
print(f"Starting gunicorn (PORT={port_int} will be read by config file)")
print("=" * 50)

# Start gunicorn
# Use execvp to replace Python process with gunicorn
os.execvp('gunicorn', gunicorn_args)

