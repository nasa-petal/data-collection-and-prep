import pandas as pd

import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = sys.argv[0],
                                     description = "read cvs, mod, and write back.")

    parser.add_argument('io_csv', type=str, help='input/output CSV file')

    args = parser.parse_args()

    df = pd.read_csv(args.io_csv)

    df.to_csv(args.io_csv, index=False)