import urllib.request
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any
import argparse
import time


def download_with_progress(url: str, output_filename: str):
    try:
        if output_filename:
            filename = output_filename
        else:
            url_path = url.split('?')[0]
            last_part = url_path.split('/')[-1]
            filename = last_part if '.' in last_part else "downloaded_file"
        filepath = Path(filename)

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        
        total_size = int(response.headers.get('Content-Length', 0))
        block_size = 8192
        downloaded = 0

        start_time = time.time()
        last_time = start_time
        last_downloaded = 0

        with open(filepath, 'wb') as f:
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                f.write(buffer)
                downloaded += len(buffer)

                current_time = time.time()

                if total_size > 0:
                    speed = (downloaded - last_downloaded) / (current_time - last_time + 1e-3)
                    last_downloaded = downloaded
                    last_time = current_time

                    if speed >= 1024*1024:
                        speed_str = f"{speed/(1024*1024):.2f} MB/s"
                    else:
                        speed_str = f"{speed/1024:.2f} KB/s"

                    eta_str = "N/A"
                    if speed > 0:
                        eta = (total_size - downloaded) / speed
                        eta_str = f"{int(eta//60)}m{int(eta % 60)}s" if eta >= 60 else f"{int(eta)}s"

                    progress = (downloaded / total_size) * 100
                    bar = '*' * int(progress // 2) + '-' * (50 - int(progress // 2))
                    print(f"\r[{bar}] {progress:.1f}% | {speed_str} | ETA: {eta_str}", end='')

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple wget-like CLI tool")
    parser.add_argument("url", nargs='?', default="https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Tux.svg/200px-Tux.svg.png", help="URL to download")
    parser.add_argument("-o", "--output", help="Output filename")
    args, unknown = parser.parse_known_args()
    
    download_with_progress(args.url, args.output)
