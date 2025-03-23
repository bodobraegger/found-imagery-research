import requests
from html.parser import HTMLParser
from urllib.parse import urljoin
import os
import sys

class DirectoryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    self.links.append(value)

def download_directory(url, output_dir='.', recursive=False):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        parser = DirectoryParser()
        parser.feed(response.text)

        os.makedirs(output_dir, exist_ok=True)

        for link in parser.links:
            if link in ['/', '../', '..', '.'] or link.startswith('?'):
                continue
            full_url = urljoin(url, link)
            # url-decode the link for easier reading
            link = requests.utils.unquote(link)

            if link.endswith('/') and recursive:
                new_dir = os.path.join(output_dir, link.rstrip('/'))
                print(f"Entering directory: {link}")
                download_directory(full_url, new_dir, recursive)
            elif not link.endswith('/'):
                print(f"Downloading: {link}")
                try:
                    file_response = requests.get(full_url, headers=HEADERS)
                    file_response.raise_for_status()

                    file_path = os.path.join(output_dir, link)
                    # if the file already exists, skip it
                    if os.path.exists(file_path):
                        print(f"File already exists: {link}")
                        continue
                    with open(file_path, 'wb') as f:
                        f.write(file_response.content)
                    print(f"Successfully downloaded: {link}")
                except Exception as e:
                    print(f"Error downloading {link}: {e}")

    except Exception as e:
        print(f"Error accessing {url}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py URL [-r] [-o OUTPUT_DIR]")
        sys.exit(1)

    url = sys.argv[1]
    recursive = '-r' in sys.argv
    
    output_dir = f"./{url.replace('http://', '').replace('https://', '').replace(':', '_')}"
    if '-o' in sys.argv:
        try:
            idx = sys.argv.index('-o')
            output_dir = sys.argv[idx + 1]
        except (IndexError, ValueError):
            print("Error: -o requires an output directory path")
            sys.exit(1)
    
    print(f"Starting download from: {url}")
    print(f"Output directory: {output_dir}")
    print(f"Recursive mode: {recursive}")
    
    download_directory(url, output_dir, recursive)
    print("Download complete!")

if __name__ == '__main__':
    main()
