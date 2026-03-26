import csv
from pathlib import Path

def write_to_csv(data: list[dict], filename: str, append: bool = False) -> None:
    """
    Escreve dados em CSV.
    
    Args:
        data: Lista de dicionários com os dados
        filename: Caminho do arquivo CSV
        append: Se True, adiciona ao final; se False, sobrescreve
    """
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if not data:
        return

    mode = "a" if append else "w"
    file_exists = filepath.exists()

    with open(filepath, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        
        # Escreve cabeçalho só se criar arquivo novo ou append=False
        if not file_exists or not append:
            writer.writeheader()
        
        writer.writerows(data)