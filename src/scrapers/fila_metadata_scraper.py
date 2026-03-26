from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from storage.metadata_writer import save_metadata_csv, save_metadata_json
from utils.headers import get_headers
from utils.delays import apply_delay

DEFAULT_METADATA_URLS = [
    "https://www.gov.br/saude/pt-br/acesso-a-informacao/sic/dados-em-transparencia-ativa",
    "https://dadosabertos.saude.gov.br/",
    "https://info.saude.df.gov.br/",
    "https://datasus.saude.gov.br/informacoes-de-saude-tabnet/",
]


def extract_page_metadata(url: str, headers: dict | None = None) -> dict:
    headers = headers or get_headers()
    base = {
        "url": url,
        "scraped_at_utc": datetime.now(timezone.utc).isoformat(),
        "status_code": None,
        "final_url": None,
        "title": None,
        "meta_description": None,
        "canonical": None,
        "table_count": 0,
        "csv_links_count": 0,
        "csv_links": "",
        "error": "",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        base["status_code"] = response.status_code
        base["final_url"] = response.url

        if response.status_code >= 400:
            base["error"] = f"HTTP {response.status_code}"
            return base

        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("title")
        base["title"] = title_tag.get_text(strip=True) if title_tag else ""

        desc_tag = soup.find("meta", attrs={"name": "description"})
        base["meta_description"] = desc_tag.get("content", "").strip() if desc_tag else ""

        canonical_tag = soup.find("link", rel="canonical")
        base["canonical"] = canonical_tag.get("href", "").strip() if canonical_tag else ""

        base["table_count"] = len(soup.find_all("table"))

        csv_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            abs_href = urljoin(response.url, href)
            if ".csv" in abs_href.lower():
                csv_links.append(abs_href)

        csv_links = sorted(set(csv_links))
        base["csv_links_count"] = len(csv_links)
        base["csv_links"] = " | ".join(csv_links)

        return base

    except Exception as e:
        base["error"] = str(e)
        return base


def collect_metadata_from_urls(urls: list[str], delay_seconds: int = 2) -> list[dict]:
    results = []
    headers = get_headers()

    for url in urls:
        print(f"[METADATA] {url}")
        item = extract_page_metadata(url, headers=headers)
        results.append(item)
        apply_delay(delay_seconds)

    return results


def run_metadata_pipeline(
    urls: list[str] | None = None,
    csv_path: str = "data/metadata/filas_sus_metadata.csv",
    json_path: str = "data/metadata/filas_sus_metadata.json",
    delay_seconds: int = 2,
) -> list[dict]:
    targets = urls or DEFAULT_METADATA_URLS
    results = collect_metadata_from_urls(targets, delay_seconds=delay_seconds)
    save_metadata_csv(results, csv_path)
    save_metadata_json(results, json_path)
    return results