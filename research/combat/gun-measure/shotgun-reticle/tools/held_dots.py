import sys, os
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr
r = sr.R5(sys.argv[1])
try:
    code = sr.DOTS.replace("{{ages}}", sys.argv[2]).replace("{{dist}}", "300").replace("{{step}}", "30").replace("{{hold}}", "6.0")
    print(r.cl(code))
    r.pl.sleep(0.5)
    r.shot("held", crop=900)
    r.pl.sleep(6)
    print([l for l in r.pl.lines["c"] if "RT" in l][-5:])
finally:
    r.close()
