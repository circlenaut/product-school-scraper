import requests
from xml.etree import ElementTree
from typing import List, Optional
from urllib.parse import urlparse

def parse_sitemap(sitemap_url: str, directories: Optional[List[str]] = None) -> List[str]:
    """
    Fetch and parse the XML sitemap, returning a list of all URLs found.
    
    Args:
        sitemap_url (str): The URL of the sitemap to parse.
        directories (Optional[List[str]]): A list of directory paths to filter URLs.
            For example, ['/blog/'] will include only URLs that start with '/blog/'.
            If None, all URLs from the sitemap are returned.
    
    Returns:
        List[str]: A list of filtered or all URLs found in the sitemap.
    """
    # Fetch the sitemap
    response = requests.get(sitemap_url)
    response.raise_for_status()

    # Parse the XML content
    root = ElementTree.fromstring(response.content)
    # Define the typical sitemap namespace
    namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'

    # Extract all URLs from the sitemap
    urls = [
        loc.text
        for loc in root.findall(f'{namespace}url/{namespace}loc')
        if loc is not None and loc.text
    ]

    # If directories are specified, filter the URLs
    if directories:
        # Normalize directories to ensure they start and end with '/'
        normalized_dirs = [dir_path if dir_path.startswith('/') else '/' + dir_path for dir_path in directories]
        normalized_dirs = [dir_path if dir_path.endswith('/') else dir_path + '/' for dir_path in normalized_dirs]

        filtered_urls = []
        for url in urls:
            parsed_url = urlparse(url)
            for dir_path in normalized_dirs:
                if parsed_url.path.startswith(dir_path):
                    filtered_urls.append(url)
                    break  # Avoid adding the same URL multiple times
        return filtered_urls

    return urls