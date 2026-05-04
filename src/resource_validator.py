import requests

def validate_url(url):
    """Validate if a URL is reachable using a HEAD request."""
    if not url or not url.startswith("http"):
        return False
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code < 400
    except requests.RequestException:
        # Fallback to GET if HEAD is not allowed
        try:
            response = requests.get(url, stream=True, timeout=5)
            return response.status_code < 400
        except:
            return False
