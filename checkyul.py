from __future__ import print_function
import sys
import subprocess
import glob
import shutil
import os

#diff $(solc --strict-assembly --optimize $INPUT_YUL 2>&1| awk '/object/,/^}$/' > topt; yulrun --input-file topt > topt.trace; echo "topt.trace") $(solc --strict-assembly $INPUT_YUL 2>&1 | awk '/object/,/^}$/' > t; yulrun --input-file t > t.trace; echo "t.trace")

compiled = 0
failed = 0
total = 0.0

def printFile(f):
    with open(f) as ff:
        for line in ff:
            print(line,end="")

def output_to_file(outfn, objfn):
    with open(outfn, 'r') as outf:
        with open(objfn, 'w') as objf:
            object = False
            for line in outf:
                if "object" in line:
                    object = True
                if object:
                    objf.write(line)
                    if line[0] == "}":
                        object = False

for f in glob.glob(sys.argv[1]):
    if "orig" in f:
        continue
    total += 1
    with open(f, 'r') as yulinf:
        with open("opttest.yul", 'w') as yuloutf:
            for line in yulinf:
                ls = line.split()
                if (len(ls) == 0) or not (ls[0].startswith("//")):
                    yuloutf.write(line)
    with open("optout.txt", 'w') as optf:
        r = subprocess.call(["/root/solidity/build/solc/solc --strict-assembly --optimize opttest.yul"], shell=True, stdout=optf, stderr=optf)
    if r == 0:
        compiled += 1
        print(f, "COMPILED; NOW UP TO", compiled, "COMPILED,", str(round((compiled/total)*100,2))+"%")
        with open("opttest.yul", 'r') as foof:
            skip = False
            for line in foof:
                if "linkersymbol" in line:
                    print("linkersymbol in Yul, skipping yulrun")
                    skip = True
                    break
            if skip:
                continue
        with open("noptout.txt",'w') as noptf:
            r = subprocess.call(["/root/solidity/build/solc/solc --strict-assembly opttest.yul"], shell=True, stdout=noptf, stderr=noptf)
        output_to_file("optout.txt", "topt")
        output_to_file("noptout.txt", "t")
        print("RUNNING OPTIMIZED...", end="")
        with open("yulrunopt.txt", 'w') as yulrunoptf:
            r = subprocess.call(["ulimit -t 10; /root/solidity/build/test/tools/yulrun --input-file topt"], shell=True, stdout=yulrunoptf, stderr=yulrunoptf)
        print("RUNNING UN-OPTIMIZED...",end="")
        with open("yulrun.txt", 'w') as yulrunf:
            r = subprocess.call(["ulimit -t 10; /root/solidity/build/test/tools/yulrun --input-file t"], shell=True, stdout=yulrunf, stderr=yulrunf)
        with open(os.devnull, 'w') as dnull:
            r = subprocess.call(["diff", "yulrunopt.txt", "yulrun.txt"], stdout=dnull, stderr=dnull)
        if (r != 0):
            with open("yulrun.txt", 'r') as yulrunf:
                skip = False
                for line in yulrunf:
                    if "Parsed successfully but had errors." in line:
                        print("PARSED BUT HAD ERRORS IN UN-OPTIMIZED, SKIPPING")
                        skip = True
                        break
                if skip:
                    continue
            failed += 1
            print("="*80)
            print("POSSIBLE OPTIMIZER BUG:\n")
            print("opttest.yul:")
            printFile("opttest.yul")
            #subprocess.call(["cat opttest.yul"], shell=True)
            print("\noptimized yul:")
            printFile("topt")
            #subprocess.call(["cat topt"], shell=True)
            print("\noptimized trace:")
            printFile("yulrunopt.txt")
            #subprocess.call(["cat yulrunopt.txt"], shell=True)
            print("\nun-optimized yul:")
            printFile("t")
            #subprocess.call(["cat t"], shell=True)
            print("\nun-optimized trace:")
            printFile("yulrun.txt")
            #subprocess.call(["cat yulrun.txt"], shell=True)
            print("="*80)
        print("DONE CHECKING")
        
print(compiled, "COMPILED")
print(failed, "FAILED")
