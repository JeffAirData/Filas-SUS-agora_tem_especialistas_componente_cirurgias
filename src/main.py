import os
from dotenv import load_dotenv

from scrapers.fila_dataset_scraper import run_fila_pipeline
from scrapers.fila_metadata_scraper import run_metadata_pipeline

load_dotenv()

def main():
    print("=" * 60)
    print("[INICIANDO] Coleta de dados públicos de filas do SUS")
    print("=" * 60)

    run_fila_pipeline()
    run_metadata_pipeline(delay_seconds=1)

    print("=" * 60)
    print("[OK] Resultados salvos em data/filas/ e data/metadata/")
    print("=" * 60)

if __name__ == "__main__":
    main()