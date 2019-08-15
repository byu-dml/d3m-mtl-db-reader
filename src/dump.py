import json
from argparse import ArgumentParser
import datetime
import os

from elasticsearch_dsl import Search
from tqdm import tqdm

from src.client import client
from src.settings import Index, DefaultDir


def get_parser() -> ArgumentParser:
    """Configures the argument parser for dumping or counting the database."""
    parser = ArgumentParser(description="Make a local dump of the D3M MtL Database.")
    parser.add_argument(
        "--out-dir",
        "-o",
        default=DefaultDir.DUMP.value,
        help=(
            "The path to the folder the dump will be "
            "written to (include the folder name)"
        ),
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=100,
        help="The number of records to read from the database at a time",
    )
    parser.add_argument(
        "--count",
        "-c",
        action="store_true",
        help=(
            "If present, the dump will not take place; only the number "
            "of records in each index will be written out."
        ),
    )
    return parser


def dump(out_dir: str, batch_size: int):
    """Read the DB indexes and dump them to :out_dir:."""
    for index in Index:
        index_name = index.value
        out_name = f"{out_dir}/{index_name}.json"

        s = Search(using=client, index=index_name)
        num_docs_in_index = s.count()
        print(
            (
                f"Now writing index '{index_name}' ({num_docs_in_index} documents) "
                f"to path '{out_name}'"
            )
        )

        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)

        with open(out_name, "w") as f:
            for hit in tqdm(s.params(size=batch_size).scan(), total=num_docs_in_index):
                # Paginate over this index
                f.write(json.dumps(hit.to_dict()))
                f.write("\n")


def count():
    """Count the number of documents in each index of the DB."""
    counts = []

    for index in Index:
        index_name = index.value
        num_docs_in_index = Search(using=client, index=index_name).count()
        counts.append((index_name, num_docs_in_index))

    print("DB index counts ({index_name}\t{count}):")
    for index, count in counts:
        print(f"{index}\t{count}")


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    if args.count:
        count()
    else:
        dump(args.out_dir, args.batch_size)
