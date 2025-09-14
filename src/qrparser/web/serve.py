# comments in English only
from __future__ import annotations

import uvicorn
from qrparser.config.settings import get_settings

def main() -> None:
    s = get_settings()
    # Settings provide host/port/workers and log level
    host = s.HTTP_HOST
    port = s.HTTP_PORT
    workers = s.HTTP_WORKERS
    log_level = s.LOG_LEVEL.lower()

    config = uvicorn.Config(
        "qrparser.web.main:create_app",  # factory target
        factory=True,
        host=host,
        port=port,
        workers=workers,
        access_log=False,
        log_config=None,     # do not override our structured logging
        log_level=log_level,
        timeout_keep_alive=30,
    )
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    main()
