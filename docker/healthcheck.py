#!/usr/bin/env python3
import sys, urllib.request
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3) as r:
        sys.exit(0 if r.status == 200 else 1)
except Exception:
    sys.exit(1)