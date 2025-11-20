"""
Gunicorn configuration file
Reads PORT from environment variable
"""
import os

# Get PORT from environment or use default
port = os.environ.get('PORT', '5000')

# Validate and convert to int
try:
    port_int = int(port)
    if port_int < 1 or port_int > 65535:
        raise ValueError(f"PORT must be between 1 and 65535, got {port_int}")
except ValueError as e:
    print(f"ERROR: Invalid PORT value: {e}")
    raise

# Bind address
bind = f"0.0.0.0:{port_int}"

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

