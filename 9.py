import urllib.request
import urllib.error
import base64
import sys
import time
import threading
import queue
from pathlib import Path
from typing import Dict, Any, Optional
import argparse


class Downloader:
    def __init__(self, url: str, output_filename: Optional[str] = None,
                 block_size: int = 262144, headers: Optional[Dict[str, Any]] = None,
                 user: Optional[str] = None, password: Optional[str] = None,
                 timeout: float = 10):
        self.url = url
        self.block_size = block_size
        self.timeout = timeout
        self.user = user
        self.password = password

        # Determine filename
        if output_filename:
            self.filename = output_filename
        else:
            url_path = url.split('?')[0]
            last_part = url_path.split('/')[-1]
            self.filename = last_part if '.' in last_part else "downloaded_file"
        self.filepath = Path(self.filename)

        # Thread-safe communication
        self.status_queue = queue.Queue()
        self.downloaded_bytes = 0
        self.total_size = 0
        self.stop_event = threading.Event()

        # Build request
        self.req = urllib.request.Request(url)
        self._setup_headers(headers or {})

    def _setup_headers(self, custom_headers: Dict[str, Any]):
        # Default browser headers to avoid 403/400
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        
        for k, v in default_headers.items():
            self.req.add_header(k, v)
            
        for k, v in custom_headers.items():
            self.req.add_header(k.strip(), v.strip())

        if self.user and self.password:
            auth_str = f"{self.user}:{self.password}".encode('utf-8')
            base64_auth = base64.b64encode(auth_str).decode('utf-8')
            self.req.add_header("Authorization", f"Basic {base64_auth}")

    def _download_worker(self):
        """Thread 1: Handles downloading and writing to disk"""
        try:
            opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
            urllib.request.install_opener(opener)
            
            response = urllib.request.urlopen(self.req, timeout=self.timeout)
            self.total_size = int(response.headers.get('Content-Length', 0))
            
            self.status_queue.put(('start', self.total_size, response.getcode()))

            with open(self.filepath, 'wb') as f:
                while not self.stop_event.is_set():
                    buffer = response.read(self.block_size)
                    if not buffer:
                        break
                    f.write(buffer)
                    self.downloaded_bytes += len(buffer)
                    self.status_queue.put(('progress', self.downloaded_bytes))

            if not self.stop_event.is_set():
                self.status_queue.put(('finished', self.downloaded_bytes))
                
        except Exception as e:
            self.status_queue.put(('error', str(e)))

    def _progress_worker(self):
        """Thread 2: Handles UI display (Progress bar, Speed, ETA)"""
        start_time = time.time()
        last_time = start_time
        last_downloaded = 0
        total_size = 0
        status_code = 0

        while not self.stop_event.is_set():
            try:
                msg_type, *data = self.status_queue.get(timeout=0.1)
                
                if msg_type == 'start':
                    total_size, status_code = data
                    print(f"HTTP Status: {status_code}")
                    
                elif msg_type == 'progress':
                    downloaded = data[0]
                    current_time = time.time()
                    
                    if total_size > 0:
                        # Speed calculation
                        time_delta = current_time - last_time
                        byte_delta = downloaded - last_downloaded
                        speed = byte_delta / time_delta if time_delta > 0 else 0
                        
                        last_time = current_time
                        last_downloaded = downloaded

                        # Format speed
                        if speed >= 1024 * 1024:
                            speed_str = f"{speed/(1024*1024):.2f} MB/s"
                        elif speed >= 1024:
                            speed_str = f"{speed/1024:.2f} KB/s"
                        else:
                            speed_str = f"{speed:.2f} B/s"

                        # ETA
                        eta = (total_size - downloaded) / speed if speed > 0 else 0
                        eta_str = f"{int(eta//60)}m{int(eta%60)}s" if eta >= 60 else f"{int(eta)}s"

                        # Progress bar
                        progress = (downloaded / total_size) * 100
                        bar = '=' * int(progress // 2) + '>' + '-' * (49 - int(progress // 2))
                        print(f"\r[{bar}] {progress:.1f}% | {speed_str} | ETA: {eta_str}", end="")

                elif msg_type == 'finished':
                    print(f"\n\nDownload completed successfully!")
                    print(f"File saved to: {self.filepath.absolute()}")
                    self.stop_event.set()
                    break

                elif msg_type == 'error':
                    error_msg = data[0]
                    print(f"\nError: {error_msg}")
                    # Re-raise error for main loop retry logic
                    self.stop_event.set()
                    raise Exception(error_msg)
                    
            except queue.Empty:
                continue
            except Exception:
                break

    def start(self):
        """Start the multi-threaded download"""
        download_thread = threading.Thread(target=self._download_worker, daemon=True)
        progress_thread = threading.Thread(target=self._progress_worker, daemon=True)

        download_thread.start()
        progress_thread.start()

        download_thread.join()
        progress_thread.join()
        
        # Check if we stopped due to error
        if not self.stop_event.is_set() or (self.total_size > 0 and self.downloaded_bytes < self.total_size):
             # If progress thread died but download didn't finish, consider it failed
             if self.downloaded_bytes == 0:
                 raise Exception("Download failed to start")


def download_with_progress_threaded(url: str, output_filename: str, retries: int, 
                                     timeout: float = 10, block_size: int = 262144,
                                     user=None, password=None, headers: Dict[str, Any] = None):
    attempt = 0
    while attempt < retries:
        try:
            print(f"Attempt {attempt+1}/{retries}")
            downloader = Downloader(
                url=url,
                output_filename=output_filename,
                block_size=block_size,
                headers=headers,
                user=user,
                password=password,
                timeout=timeout
            )
            downloader.start()
            return

        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed")
            if attempt < retries:
                print(f"Retrying in 2 seconds... ({retries - attempt} attempts left)\n")
                time.sleep(2)

    print(f"\nAll {retries} attempts failed. Download aborted.")
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple wget-like CLI tool (Stage 9: Threaded)")
    parser.add_argument("url", nargs='?', 
                       default="https://upload.wikimedia.org/wikipedia/commons/3/35/Tux.svg", 
                       help="URL to download")
    parser.add_argument("-o", "--output", help="Output filename")
    parser.add_argument("-r", "--retry", type=int, default=3, help="Number of retries (default: 3)")
    parser.add_argument("--user", help="Username for basic authentication")
    parser.add_argument("--password", help="Password for basic authentication")
    parser.add_argument("--header", action="append", help="Custom header (e.g., --header 'Key: Value')")
    parser.add_argument("--bufsize", type=int, default=262144, 
                       help="Buffer/Block size in bytes (default: 262144 = 256KB, Stage 9 optimization)")

    args, unknown = parser.parse_known_args()

    custom_headers = {}
    if args.header:
        for h in args.header:
            try:
                key, value = h.split(':', 1)
                custom_headers[key] = value
            except ValueError:
                print(f"Invalid header format: {h}")

    download_with_progress_threaded(
        url=args.url,
        output_filename=args.output,
        retries=args.retry,
        timeout=10,
        block_size=args.bufsize,
        user=args.user,
        password=args.password,
        headers=custom_headers
    )
