"""
Gunicorn configuration file
Reads PORT from environment variable
"""
import os
import sys

# DEBUG: Log environment
print("=" * 50)
print("DEBUG: Gunicorn config file loading")
print("=" * 50)
port_env = os.environ.get('PORT')
print(f"DEBUG: PORT from environment: {repr(port_env)} (type: {type(port_env).__name__})")

# Get PORT from environment or use default
port = os.environ.get('PORT', '5000')
print(f"DEBUG: PORT value after get: {repr(port)}")

# Validate and convert to int
try:
    port_int = int(port)
    print(f"DEBUG: PORT converted to int: {port_int}")
    if port_int < 1 or port_int > 65535:
        raise ValueError(f"PORT must be between 1 and 65535, got {port_int}")
except ValueError as e:
    print(f"ERROR: Invalid PORT value: {e}")
    print(f"ERROR: PORT raw value: {repr(port)}")
    sys.exit(1)

# Bind address - MUST be a string with format "host:port"
bind = f"0.0.0.0:{port_int}"
print(f"DEBUG: Bind address: {repr(bind)}")

# Worker configuration
workers = 1
timeout = 300
graceful_timeout = 120
keepalive = 5

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

print(f"Gunicorn config: bind={bind}, workers={workers}, timeout={timeout}")
print("=" * 50)

