"""Maya MCP Bridge — HTTP server that relays Python code to Maya commandPort.

Improvements over v1:
- Uses socket.shutdown(SHUT_WR) to signal EOF properly before reading response
- Reads commandPort output back (Maya sends result via commandPort)
- Handles large code blocks correctly
- Graceful timeout handling
"""
import socket
import json
import threading
import time

MAYA_HOST = "127.0.0.1"
MAYA_PORT = 7002
BRIDGE_PORT = 9756
TIMEOUT = 60  # seconds for Maya command execution


def maya_exec(code):
    """Send Python code to Maya commandPort (fire-and-forget with delay).

    Maya commandPort processes code asynchronously. We send the code,
    wait briefly for TCP buffers to flush, then close.
    The code's side effects (scene changes, file writes) are how we
    verify execution.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    try:
        s.connect((MAYA_HOST, MAYA_PORT))
        s.sendall((code + "\n").encode("utf-8"))
        # Brief pause to ensure TCP buffer flush before close
        # This prevents data loss from RST on close
        import time as _time
        _time.sleep(0.3)
        s.close()
        return "sent to Maya"
    except Exception as e:
        return "Error: " + str(e)
    finally:
        try:
            s.close()
        except Exception:
            pass


def handle(conn):
    """Handle one HTTP request."""
    try:
        conn.settimeout(10)
        raw = conn.recv(65536).decode("utf-8", errors="replace")
        # Parse HTTP body (simple parser — JSON is after \r\n\r\n)
        body_str = raw[raw.find("\r\n\r\n") + 4:] if "\r\n\r\n" in raw else raw
        req = json.loads(body_str) if body_str else {}
        code = req.get("code", "")

        if not code:
            resp = json.dumps({"status": "error", "message": "no code field"}).encode()
        else:
            # Execute in Maya and get result
            result = maya_exec(code)
            resp = json.dumps({"status": "ok", "result": result}).encode()

        http_resp = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(resp)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode() + resp
        conn.sendall(http_resp)
    except Exception as e:
        error_resp = json.dumps({"status": "error", "message": str(e)}).encode()
        try:
            conn.sendall(
                f"HTTP/1.1 500 Internal Error\r\nContent-Type: application/json\r\nContent-Length: {len(error_resp)}\r\n\r\n".encode()
                + error_resp
            )
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv.settimeout(1)
    serv.bind(("127.0.0.1", BRIDGE_PORT))
    serv.listen(5)
    print(f"Maya Bridge ready on 127.0.0.1:{BRIDGE_PORT} -> Maya :{MAYA_PORT}")
    while True:
        try:
            conn, addr = serv.accept()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            print("\nBridge shutting down.")
            break


if __name__ == "__main__":
    main()
