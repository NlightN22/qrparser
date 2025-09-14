from __future__ import annotations
import uvicorn

def main() -> None:
    config = uvicorn.Config(
        "qrparser.web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,         # dev only
        access_log=False,    # no duplicate access logs
        log_config=None,     # <<< key: do NOT let uvicorn configure logging
        log_level="info",    # level still respected by uvicorn loggers
    )
    server = uvicorn.Server(config)
    try:
        server.run()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
