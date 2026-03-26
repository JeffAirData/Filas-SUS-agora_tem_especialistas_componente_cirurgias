import requests
from bs4 import BeautifulSoup

def scrape_static(url: str, headers: dict | None = None) -> list[dict]:
    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 401:
        print(f"[WARN] 401 Unauthorized (sem sessão/autenticação): {url}")
        return []

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    titulos = [h.get_text(strip=True) for h in soup.find_all("h2")]
    return [{"url": url, "titulo": t} for t in titulos]