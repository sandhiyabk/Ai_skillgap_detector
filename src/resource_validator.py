import requests

def validate_url(url):
    """Validate if a URL is reachable using a HEAD request."""
    if not url or not url.startswith("http"):
        return False
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.head(url, allow_redirects=True, timeout=5, headers=headers)
        return response.status_code < 400 or response.status_code in (401, 403)
    except requests.RequestException:
        # Fallback to GET if HEAD is not allowed
        try:
            response = requests.get(url, stream=True, timeout=5, headers=headers)
            return response.status_code < 400 or response.status_code in (401, 403)
        except:
            return False
