import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "qrparser.web.main:app",
        reload=True,
        reload_dirs=["src", "tests"],
        host="127.0.0.1",
        port=8000,
    )