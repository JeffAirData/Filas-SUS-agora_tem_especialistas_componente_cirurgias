import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scrapers.fila_dataset_scraper import run_fila_pipeline


if __name__ == "__main__":
    run_fila_pipeline()
