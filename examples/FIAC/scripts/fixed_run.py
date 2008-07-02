"""
Perform a fixed run of FIAC model

python fixed_run.py [subject]

"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import fixed, io


def run(subj):
    os.system("rm %s/fixed/*/*/*/fiac%d/*bz2" % (io.data_path, subj))
    try:
        fixed.run(subj=subj)
    except:
        pass
    os.system("bzip2 %s/fixed/*/*/*/fiac%d/*nii" % (io.data_path, subj))
    

if __name__ == "__main__":
    if len(sys.argv) == 2:
        subject = int(sys.argv[1])
    else:
        subject = 1
    run(subject)