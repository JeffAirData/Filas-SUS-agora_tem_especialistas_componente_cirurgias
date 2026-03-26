import argparse
from pathlib import Path
import pandas as pd

try:
    from pysus.utilities.readdbc import read_dbc
    HAS_PYSUS = True
except ImportError:
    HAS_PYSUS = False

def convert_dbc_pysus(input_file: Path, output_file: Path) -> bool:
    """Converte usando pysus"""
    if not HAS_PYSUS:
        return False
    
    try:
        df = read_dbc(str(input_file), encoding="latin-1")
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"[OK] {output_file} ({len(df)} linhas)")
        return True
    except Exception as e:
        print(f"[ERRO] pysus: {e}")
        return False

def convert_dbc_fallback(input_file: Path, output_file: Path) -> bool:
    """Fallback: registra arquivo para conversão manual"""
    print(f"[WARN] Instale pysus para converter: {input_file}")
    print(f"       pip install pysus")
    with open("data/dbc_pendentes.txt", "a", encoding="utf-8") as f:
        f.write(f"{input_file}\n")
    return False

def main():
    parser = argparse.ArgumentParser(description="Converte .dbc DATASUS para CSV")
    parser.add_argument("input", help="Arquivo .dbc ou pasta com .dbc")
    parser.add_argument("--output", default="data/dbc_csv", help="Pasta de saída")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = []
    if input_path.is_file() and input_path.suffix.lower() == ".dbc":
        files = [input_path]
    elif input_path.is_dir():
        files = sorted(input_path.glob("**/*.dbc"))
    else:
        print(f"[ERRO] Entrada inválida: {input_path}")
        return

    for dbc_file in files:
        csv_file = output_dir / f"{dbc_file.stem}.csv"
        
        if not convert_dbc_pysus(dbc_file, csv_file):
            convert_dbc_fallback(dbc_file, csv_file)

if __name__ == "__main__":
    main()