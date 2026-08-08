import uvicorn
import os
import threading
import time
import webbrowser


def browser_launch_enabled() -> bool:
    """The add-on runs headless, so the browser launch is switched off there."""
    return not os.environ.get("CATLABEL_NO_BROWSER")


def open_browser_when_ready(
    server,
    port: int,
    *,
    poll_interval: float = 0.1,
    browser_open=None,
    sleeper=None,
) -> bool:
    """Open CatLabel only after Uvicorn has completed application startup."""
    browser_open = browser_open or webbrowser.open
    sleeper = sleeper or time.sleep

    while not server.started:
        if server.should_exit:
            return False
        sleeper(poll_interval)

    browser_open(f"http://localhost:{port}")
    return True


def main() -> None:
    port = int(os.environ.get("CATLABEL_PORT", 8000))
    config = uvicorn.Config(
        "catlabel.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
    server = uvicorn.Server(config)
    if browser_launch_enabled():
        threading.Thread(
            target=open_browser_when_ready,
            args=(server, port),
            daemon=True,
        ).start()
    server.run()


if __name__ == "__main__":
    main()
