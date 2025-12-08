#!/usr/bin/env python3
"""
Simple HTTP server to view the workflow dashboard.
This is needed because browsers block loading local CSV files for security reasons.
"""
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8000

# Change to script directory
os.chdir(Path(__file__).parent)

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow CSV loading
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        # Cleaner logging
        if '200' in str(args):
            print(f"✓ Loaded: {args[0]}")

print("=" * 60)
print("  Workflow Dashboard Server")
print("=" * 60)
print(f"\n🚀 Starting server at http://localhost:{PORT}")
print(f"📁 Serving files from: {os.getcwd()}")
print(f"\n📊 Opening dashboard in your browser...")
print(f"\n⚠️  Press Ctrl+C to stop the server\n")
print("=" * 60 + "\n")

Handler = MyHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    # Open browser
    webbrowser.open(f'http://localhost:{PORT}/workflow_dashboard.html')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("  Server stopped")
        print("=" * 60)
