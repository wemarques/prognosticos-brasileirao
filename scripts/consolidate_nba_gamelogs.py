"""
Consolida gamelogs de jogadores da NBA a partir de múltiplos CSVs.

Uso (a partir da raiz do repo):
  python scripts/consolidate_nba_gamelogs.py

Por padrão, lê:  nba/gamelogs/*.csv
E gera:          NBA_PLAYER_GAMELOG_2025_26.csv
"""

from __future__ import annotations

import argparse
import glob
import os
from typing import Iterable, List

import pandas as pd


EXPECTED_COLS: List[str] = [
    "Rk",
    "Gcar",
    "Gtm",
    "Date",
    "Team",
    "Opp",
    "Result",
    "GS",
    "MP",
    "FG",
    "FGA",
    "FG%",
    "3P",
    "3PA",
    "3P%",
    "2P",
    "2PA",
    "2P%",
    "eFG%",
    "FT",
    "FTA",
    "FT%",
    "ORB",
    "DRB",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PTS",
    "GmSc",
    "+/-",
]


def _iter_input_files(input_glob: str) -> List[str]:
    files = sorted(glob.glob(input_glob))
    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo encontrado para o padrão: {input_glob!r}. "
            "Verifique o caminho/glob de entrada."
        )
    return files


def _read_and_validate(file_path: str, expected_cols: List[str]) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    # remove coluna vazia automaticamente (ex: Unnamed: 0)
    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]

    # validação rígida: mesma ordem e mesmo conjunto
    if list(df.columns) != expected_cols:
        raise ValueError(
            f"Layout inválido em {file_path}\n"
            f"Esperado: {expected_cols}\n"
            f"Encontrado: {list(df.columns)}"
        )

    player_id = os.path.splitext(os.path.basename(file_path))[0]
    df.insert(0, "player_id", player_id)
    return df


def consolidate_nba_gamelogs(
    input_glob: str = "nba/gamelogs/*.csv",
    output_csv: str = "NBA_PLAYER_GAMELOG_2025_26.csv",
    drop_duplicates: bool = True,
    expected_cols: List[str] | None = None,
) -> str:
    expected = expected_cols if expected_cols is not None else EXPECTED_COLS
    files = _iter_input_files(input_glob)

    dfs: List[pd.DataFrame] = []
    for file_path in files:
        dfs.append(_read_and_validate(file_path, expected))

    df_all = pd.concat(dfs, ignore_index=True)
    if drop_duplicates:
        df_all = df_all.drop_duplicates()

    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    df_all.to_csv(output_csv, index=False)
    return output_csv


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Consolida CSVs de gamelog NBA em um único arquivo.")
    p.add_argument(
        "--input-glob",
        default="nba/gamelogs/*.csv",
        help="Padrão (glob) para localizar arquivos CSV de entrada.",
    )
    p.add_argument(
        "--output",
        default="NBA_PLAYER_GAMELOG_2025_26.csv",
        help="Caminho do CSV de saída.",
    )
    p.add_argument(
        "--no-drop-duplicates",
        action="store_true",
        help="Não remove duplicatas exatas ao final.",
    )
    return p


def main(argv: Iterable[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv) if argv is not None else None)
    out = consolidate_nba_gamelogs(
        input_glob=args.input_glob,
        output_csv=args.output,
        drop_duplicates=not args.no_drop_duplicates,
    )
    print(f"Arquivo unificado criado com sucesso: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

