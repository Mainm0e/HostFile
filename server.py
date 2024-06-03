import http.server
import socketserver
import os
import asyncio
import websockets

PORT = 8000
DIRECTORY = "downloads"
FILENAME = "example.txt"
CONTENT = "This is a sample file."

# Create the directory if it doesn't exist
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)
    print(f"Created directory: {DIRECTORY}")

# Create the file if it doesn't exist
file_path = os.path.join(DIRECTORY, FILENAME)
if not os.path.isfile(file_path):
    with open(file_path, 'w') as f:
        f.write(CONTENT)
    print(f"Created file: {file_path}")

# WebSocket server to notify clients of updates
async def notify_clients():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever

async def handler(websocket, path):
    # Notify client of update
    await websocket.send("update")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        
        if self.path == '/index.html':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_content = self.generate_html()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            super().do_GET()

    def generate_html(self):
        files = os.listdir(DIRECTORY)
        files_list_items = "\n".join(
            [f'<li>{file} <a href="/{DIRECTORY}/{file}" download="{file}"><button>Download</button></a></li>' for file in files]
        )
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>File Download</title>
            <script>
                var ws = new WebSocket("ws://localhost:8765");
                ws.onmessage = function(event) {{
                    if (event.data === 'update') {{
                        location.reload();
                    }}
                }};
            </script>
        </head>
        <body>
            <h1>Download Files</h1>
            <ul>
                {files_list_items}
            </ul>
        </body>
        </html>
        """

# Start WebSocket server
asyncio.ensure_future(notify_clients())

# Start HTTP server
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving HTTP on port {PORT} (http://localhost:{PORT}/)")
    httpd.serve_forever()
