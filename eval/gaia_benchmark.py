import os

import datasets
from dotenv import load_dotenv
from pprint import pp

load_dotenv()

gaia_benchmark = datasets.load_dataset(
    "gaia-benchmark/GAIA",
    '2023_all',
    cache_dir="../data/gaia-benchmark",
    token=os.getenv("HF_API_TOKEN"),
    trust_remote_code=True
)

gaia_benchmark_test_set = gaia_benchmark['test']

for example in gaia_benchmark_test_set:
    pp(example)
    print(example.keys())
    exit()