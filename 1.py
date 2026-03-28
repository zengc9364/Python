import urllib.request
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any
import urllib.request
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any


def downlaod_file(url: str):
    try:
        url_path = url.split('?')[0]
        last_part = url_path.split('/')[-1]
        if '.' in last_part:
            filename = last_part
        else:
            filename = "downloaded_file"
        filepath = Path(filename)
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Tux.svg/200px-Tux.svg.png"
    downlaod_file(url)

def downlaod_file(url: str):
    try:
        url_path = url.split('?')[0]
        last_part = url_path.split('/')[-1]
        if '.' in last_part:
            filename = last_part
        else:
            filename = "downloaded_file"
        filepath = Path(filename)
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Tux.svg/200px-Tux.svg.png"
    downlaod_file(url)
