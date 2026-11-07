import sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr
r = sr.R5(sys.argv[1])
try:
    r.shot("blank", crop=900)
finally:
    r.close()
