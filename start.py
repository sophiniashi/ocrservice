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

# Build bind address as string (not using $PORT variable)
bind_address = f'0.0.0.0:{port_int}'
print(f"DEBUG: Bind address: {repr(bind_address)}")

# Use gunicorn with direct arguments (no config file to avoid Railway parsing issues)
# Gunicorn auto-loads gunicorn.conf.py or gunicorn.py if present
# We ensure no config file exists, so we pass all options directly
# Pass bind address directly as argument
gunicorn_args = [
    'gunicorn',
    '-w', '1',
    '-b', bind_address,  # Pass as separate argument, not in string
    'app:app',
    '--timeout', '300',
    '--graceful-timeout', '120',
    '--keep-alive', '5'
]

# Verify no config files exist in current directory
import glob
config_files = glob.glob('gunicorn*.py') + glob.glob('gunicorn*.conf')
if config_files:
    print(f"WARNING: Found config files: {config_files}")
    print("WARNING: These will be ignored, using command line arguments only")

print(f"DEBUG: Gunicorn command: {' '.join(gunicorn_args)}")
print(f"DEBUG: Gunicorn args list: {gunicorn_args}")
print("=" * 50)
print(f"Starting gunicorn on port {port_int}")
print("=" * 50)

# Verify gunicorn is available
import shutil
gunicorn_path = shutil.which('gunicorn')
if not gunicorn_path:
    print("ERROR: gunicorn not found in PATH")
    print(f"ERROR: PATH: {os.environ.get('PATH', 'not set')}")
    sys.exit(1)
print(f"DEBUG: Found gunicorn at: {gunicorn_path}")

# Verify app.py exists
if not os.path.exists('app.py'):
    print("ERROR: app.py not found in current directory")
    print(f"ERROR: Current directory: {os.getcwd()}")
    print(f"ERROR: Files in directory: {os.listdir('.')}")
    sys.exit(1)
print("DEBUG: app.py found")

# Start gunicorn
# Use execvp to replace Python process with gunicorn
# This ensures no shell expansion happens
print("DEBUG: About to exec gunicorn...")
print(f"DEBUG: Working directory: {os.getcwd()}")
os.execvp('gunicorn', gunicorn_args)

