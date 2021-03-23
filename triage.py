import subprocess

import subprocess
import sys

with open("fuzzers.txt", 'w') as fout:
    subprocess.call(["docker", "ps"], stdout=fout, stderr=fout)

fuzzers =[]

with open("fuzzers.txt", 'r') as fout:
    for line in fout:
        if "fuzz_solc_yul" in line:
           fuzzers.append(line.split()[-1])

for docker_ps in fuzzers:
    print("*"*80)
    print("FUZZER:", docker_ps)
    subprocess.call(["source triage.sh " + docker_ps], shell=True)
    print()

subprocess.call(["yes | docker system prune"], shell=True)
