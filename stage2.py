# stage2.py
import argparse
import requests

parser = argparse.ArgumentParser(description="Simple wget clone")
parser.add_argument("url", help="URL to download")
parser.add_argument("-o", "--output", help="Output file name")

# args = parser.parse_args()  
args = parser.parse_args([
    "https://raw.githubusercontent.com/python/cpython/main/README.rst", 
    # "-o", "custom_filename.rst"  
])

filename = args.output if args.output else args.url.split('/')[-1]

print(f"Downloading to {filename}...")
response = requests.get(args.url)

with open(filename, 'wb') as f:
    f.write(response.content)
    
print("Done.")
