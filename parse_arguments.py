# myscript.py
import argparse
from typing import List

def parse_args():
    parser = argparse.ArgumentParser(
        description="Process an input string a given number of times."
    )
    parser.add_argument(
        "--description", "-d",
        type=str,
        help="Description of interactive story",
        default=None,
    )

    parser.add_argument(
        "--n-scenes", "-n",
        type=int,
        help="Number of scenes to generate",
        default=5,
    )

    parser.add_argument(
        "--leaf-probabilities", "-lp",
        nargs="+",
        help="list of leaf probabilities in the form of '2:0.2 3:0.3' (1:0.5 is inferred automatically by subtracting the sum of the others)",
        required=True,
        default=None,
    )
    # parser.add_argument(
    #     "--verbose", "-v",
    #     action="store_true",
    #     help="Print extra debugging information"
    # )
    return parser.parse_args()