import uvicorn
import os
import threading
import time
import webbrowser

def open_browser(port):
    time.sleep(5)
    webbrowser.open(f"http://localhost:{port}")

if __name__ == "__main__":
    port = int(os.environ.get("CATLABEL_PORT", 8000))
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    uvicorn.run("catlabel.api.main:app", host="0.0.0.0", port=port, reload=False)
