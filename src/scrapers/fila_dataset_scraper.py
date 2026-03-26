import csv
import io
import json
import re
import shutil
import zipfile
from pathlib import Path

import requests

SOURCE_URLS = [
    "https://www.gov.br/saude/pt-br/acesso-a-informacao/sic/dados-em-transparencia-ativa",
    "https://dadosabertos.saude.gov.br/",
    "https://info.saude.df.gov.br/",
    "https://datasus.saude.gov.br/informacoes-de-saude-tabnet/",
]

DATASET_SEARCH_QUERIES = [
    "fila",
    "espera",
    "cirurgia",
    "cirurgias",
    "lista de espera",
    "tempo de espera",
    "programa nacional de reducao das filas",
    "componente cirurgias",
]

HIGH_RELEVANCE_REQUIRED_TERMS = {
    "fila",
    "espera",
    "cirurgia",
    "cirurgias",
    "lista de espera",
    "tempo de espera",
    "programa nacional de reducao das filas",
    "componente cirurgias",
    "pnrf",
}

HIGH_RELEVANCE_CONTEXT_TERMS = {
    "agora tem especialistas",
    "procedimentos cirurgicos",
    "cirurgias previstas",
    "cirurgias realizadas",
}

MEDIUM_RELEVANCE_TERMS = {
    "samu",
    "upa",
    "regulacao",
    "regulacao assistencial",
    "leito",
    "uti",
}

LOW_RELEVANCE_TERMS = {
    "prep",
    "pep",
    "profilaxia",
    "covid-19",
    "covid 19",
    "mais medicos",
    "programa mais medicos",
    "provimento federal",
}

ALLOWED_RESOURCE_FORMATS = {"csv", "json", "xml"}
ALLOWED_EXTRACTED_SUFFIXES = {".csv", ".json", ".xml"}
RAW_BINARY_EXTENSIONS = {".zip", ".csv", ".json", ".xml"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def _normalize(text: str) -> str:
    text = (text or "").strip().lower()
    replacements = {
        "a": "[áàãâ]",
        "e": "[éê]",
        "i": "[í]",
        "o": "[óôõ]",
        "u": "[ú]",
        "c": "[ç]",
    }
    for plain, pattern in replacements.items():
        text = re.sub(pattern, plain, text)
    return re.sub(r"\s+", " ", text)


def _safe_name(text: str) -> str:
    text = _normalize(text)
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "arquivo"


def _fetch(url: str, *, stream: bool = False) -> requests.Response:
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=60,
        allow_redirects=True,
        stream=stream,
    )
    response.raise_for_status()
    return response


def _load_next_data(url: str) -> dict:
    response = _fetch(url)
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        response.text,
        re.DOTALL,
    )
    if not match:
        raise ValueError(f"Nao foi possivel localizar __NEXT_DATA__ em {url}")
    return json.loads(match.group(1))


def _classify_text(text: str) -> str:
    normalized = _normalize(text)

    if any(term in normalized for term in LOW_RELEVANCE_TERMS):
        return "low"
    if any(term in normalized for term in HIGH_RELEVANCE_REQUIRED_TERMS):
        return "high"
    if (
        any(term in normalized for term in HIGH_RELEVANCE_CONTEXT_TERMS)
        and any(term in normalized for term in {"fila", "espera", "cirurg"})
    ):
        return "high"
    if any(term in normalized for term in MEDIUM_RELEVANCE_TERMS):
        return "medium"
    return "low"


def search_dataset_packages() -> list[dict]:
    packages_by_name = {}

    for query in DATASET_SEARCH_QUERIES:
        url = f"https://dadosabertos.saude.gov.br/dataset?q={query}"
        try:
            data = _load_next_data(url)
            page_props = data.get("props", {}).get("pageProps", {})
            for package in page_props.get("packages", []):
                name = package.get("name")
                if not name:
                    continue
                packages_by_name.setdefault(name, package)
        except Exception as exc:
            print(f"[WARN] Busca no portal falhou ({query}): {exc}")

    return list(packages_by_name.values())


def enrich_package_details(package_name: str) -> dict:
    data = _load_next_data(f"https://dadosabertos.saude.gov.br/dataset/{package_name}")
    return data.get("props", {}).get("pageProps", {})


def collect_high_relevance_datasets() -> tuple[list[dict], list[dict]]:
    datasets = []
    resources = []

    for package in search_dataset_packages():
        combined_text = " ".join(
            [
                package.get("title", ""),
                package.get("notes", ""),
                package.get("name", ""),
            ]
        )
        relevance = _classify_text(combined_text)
        if relevance != "high":
            continue

        try:
            details = enrich_package_details(package["name"])
        except Exception as exc:
            print(f"[WARN] Detalhes do dataset falharam ({package['name']}): {exc}")
            continue

        dataset_row = {
            "dataset_name": details.get("name", package.get("name", "")),
            "dataset_title": details.get("title", package.get("title", "")),
            "dataset_url": f"https://dadosabertos.saude.gov.br/dataset/{package['name']}",
            "relevance": relevance,
            "notes": (details.get("notes") or "").replace("\n", " ").strip(),
            "organization": (details.get("organization") or {}).get("title", ""),
            "num_resources": details.get("num_resources", 0),
            "metadata_created": details.get("metadata_created", ""),
            "metadata_modified": details.get("metadata_modified", ""),
        }
        datasets.append(dataset_row)

        for resource in details.get("resources", []):
            resource_format = (resource.get("format") or "").strip().lower()
            if resource_format not in ALLOWED_RESOURCE_FORMATS:
                continue

            resources.append(
                {
                    "dataset_name": dataset_row["dataset_name"],
                    "dataset_title": dataset_row["dataset_title"],
                    "dataset_url": dataset_row["dataset_url"],
                    "resource_id": resource.get("id", ""),
                    "resource_name": resource.get("name", ""),
                    "resource_description": (resource.get("description") or "").replace("\n", " ").strip(),
                    "resource_format": resource_format,
                    "resource_mimetype": resource.get("mimetype", ""),
                    "resource_url": resource.get("url", ""),
                    "relevance": relevance,
                }
            )

    return datasets, resources


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        if path.exists():
            path.unlink()
        return

    with open(path, "w", newline="", encoding="utf-8-sig") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _is_probable_html(payload: bytes) -> bool:
    preview = payload[:1024].decode("utf-8", errors="ignore").lower()
    return "<html" in preview or "<!doctype html" in preview


def _extract_zip_members(raw_bytes: bytes, extract_dir: Path, dataset_slug: str, resource_slug: str) -> list[str]:
    extracted_paths = []
    target_dir = extract_dir / dataset_slug / resource_slug
    target_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as archive:
        for member in archive.infolist():
            member_name = Path(member.filename)
            if member.is_dir() or member_name.suffix.lower() not in ALLOWED_EXTRACTED_SUFFIXES:
                continue

            destination = target_dir / member_name.name
            with archive.open(member) as src, open(destination, "wb") as dst:
                shutil.copyfileobj(src, dst)
            extracted_paths.append(str(destination))

    return extracted_paths


def download_resources(resources: list[dict], raw_dir: Path, extract_dir: Path) -> list[dict]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    extract_dir.mkdir(parents=True, exist_ok=True)
    downloads = []

    for resource in resources:
        resource_url = resource["resource_url"]
        dataset_slug = _safe_name(resource["dataset_name"])
        resource_slug = _safe_name(resource["resource_name"] or resource_url)
        resource_slug = f"{resource_slug}_{resource['resource_format']}"

        try:
            response = _fetch(resource_url)
            payload = response.content
            content_type = (response.headers.get("content-type") or "").lower()
            saved_as = ""
            extracted = []

            if _is_probable_html(payload):
                raise ValueError("resposta HTML recebida em vez de artefato de dados")

            suffix = Path(resource_url).suffix.lower()
            if suffix == ".zip" or resource["resource_mimetype"] == "application/zip":
                saved_path = raw_dir / f"{dataset_slug}__{resource_slug}.zip"
                with open(saved_path, "wb") as file_obj:
                    file_obj.write(payload)
                saved_as = str(saved_path)
                extracted = _extract_zip_members(payload, extract_dir, dataset_slug, resource_slug)
                if not extracted:
                    raise ValueError("zip sem arquivos de dados extraiveis")
            else:
                if suffix not in RAW_BINARY_EXTENSIONS:
                    suffix = f".{resource['resource_format']}"
                saved_path = raw_dir / f"{dataset_slug}__{resource_slug}{suffix}"
                with open(saved_path, "wb") as file_obj:
                    file_obj.write(payload)
                saved_as = str(saved_path)
                if suffix in ALLOWED_EXTRACTED_SUFFIXES:
                    extracted_dir = extract_dir / dataset_slug / resource_slug
                    extracted_dir.mkdir(parents=True, exist_ok=True)
                    extracted_path = extracted_dir / saved_path.name
                    shutil.copy2(saved_path, extracted_path)
                    extracted.append(str(extracted_path))

            status = "downloaded" if extracted else "downloaded_without_extract"
            print(f"[OK] Recurso: {resource_url}")
        except Exception as exc:
            saved_as = ""
            extracted = []
            content_type = ""
            status = f"error: {exc}"
            print(f"[ERRO] Recurso: {resource_url} -> {exc}")

        downloads.append(
            {
                **resource,
                "saved_as": saved_as,
                "extracted_paths": " | ".join(extracted),
                "status": status,
                "content_type": content_type,
            }
        )

    return downloads


def build_extracted_inventory(extract_dir: Path) -> list[dict]:
    inventory = []
    if not extract_dir.exists():
        return inventory

    for path in sorted(extract_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in ALLOWED_EXTRACTED_SUFFIXES:
            continue

        row_count = ""
        column_names = ""

        if path.suffix.lower() == ".csv":
            try:
                with open(path, newline="", encoding="utf-8-sig") as file_obj:
                    reader = csv.DictReader(file_obj)
                    rows = list(reader)
                    row_count = len(rows)
                    column_names = " | ".join(reader.fieldnames or [])
            except Exception as exc:
                row_count = ""
                column_names = f"erro: {exc}"

        inventory.append(
            {
                "file_path": str(path),
                "extension": path.suffix.lower(),
                "row_count": row_count,
                "columns": column_names,
            }
        )

    return inventory


def cleanup_obsolete_outputs(base_dir: Path) -> None:
    obsolete_files = [
        base_dir / "discovered_pages.csv",
        base_dir / "discovered_assets.csv",
        base_dir / "api_dados_abertos_tabelas.csv",
    ]
    obsolete_dirs = [
        base_dir / "tables",
        base_dir / "sistemas_informacoes_sus_csv",
    ]

    for path in obsolete_files:
        if path.exists():
            path.unlink()

    for path in obsolete_dirs:
        if path.exists():
            shutil.rmtree(path)


def reset_output_dirs(*paths: Path) -> None:
    for path in paths:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def run_fila_pipeline() -> None:
    base_dir = Path("data/filas")
    datasets_csv = base_dir / "analytical_datasets.csv"
    resources_csv = base_dir / "analytical_resources.csv"
    downloads_csv = base_dir / "downloads.csv"
    inventory_csv = base_dir / "extracted_inventory.csv"
    raw_dir = base_dir / "raw"
    extracted_dir = base_dir / "extracted"

    cleanup_obsolete_outputs(base_dir)
    reset_output_dirs(raw_dir, extracted_dir)

    datasets, resources = collect_high_relevance_datasets()
    _write_csv(datasets_csv, datasets)
    _write_csv(resources_csv, resources)

    downloads = download_resources(resources, raw_dir, extracted_dir)
    _write_csv(downloads_csv, downloads)

    inventory = build_extracted_inventory(extracted_dir)
    _write_csv(inventory_csv, inventory)
