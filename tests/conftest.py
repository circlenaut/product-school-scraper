import pytest

@pytest.fixture(scope="session")
def sitemap_url():
    return "https://productschool.com/sitemap.xml"

@pytest.fixture(scope="session")
def sample_sitemap_xml():
    return """
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" 
            xmlns:xhtml="http://www.w3.org/1999/xhtml" 
            xmlns:news="http://www.google.com/schemas/sitemap-news/0.9" 
            xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" 
            xmlns:video="http://www.google.com/schemas/sitemap-video/1.1" 
            xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0">
        <url>
            <loc>https://productschool.com/</loc>
            <lastmod>2024-12-29T01:09:10.504Z</lastmod>
            <changefreq>daily</changefreq>
            <priority>0.7</priority>
        </url>
        <url>
            <loc>https://productschool.com/about</loc>
            <lastmod>2024-01-24T11:48:11.419Z</lastmod>
            <changefreq>daily</changefreq>
            <priority>0.7</priority>
        </url>
        <url>
            <loc>https://productschool.com/artificial-intelligence-product-certification</loc>
            <lastmod>2024-08-07T15:28:21.333Z</lastmod>
            <changefreq>daily</changefreq>
            <priority>0.7</priority>
        </url>
        <!-- Add more URLs as needed for testing -->
    </urlset>
    """