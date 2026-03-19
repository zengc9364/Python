# stage1.py
import sys
import requests

url = "https://raw.githubusercontent.com/python/cpython/main/README.rst"
filename = url.split('/')[-1] or "download.file"

print(f"Downloading {url}...")
response = requests.get(url)

with open(filename, 'wb') as f:
    f.write(response.content)
    
print("Done.")
