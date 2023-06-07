import os, shutil
from resbibman.core.compressTools import compressSelected, decompressDir


this_dir = os.path.dirname(os.path.abspath(__file__))

tmp_dir = os.path.join(this_dir, ".TempDir")
input_dir = os.path.join(tmp_dir, "input")
output_file = os.path.join(tmp_dir, "test.zip")
output_dir = os.path.join(tmp_dir, "output")
if os.path.exists(tmp_dir): 
    shutil.rmtree(tmp_dir)

os.mkdir(tmp_dir)
os.mkdir(input_dir)
os.mkdir(output_dir)

# generate some files
for i in range(10):
    with open(os.path.join(input_dir, "file"+str(i)+".txt"), "w") as f:
        f.write("Hello world from input!")
# generate some dirs
for i in range(10):
    os.mkdir(os.path.join(input_dir, "dir"+str(i)))
    with open(os.path.join(input_dir, "dir"+str(i), "file"+str(i)+".txt"), "w") as f:
        f.write("Hello world from input dir!")

root_dir = input_dir

selected = ["file1.txt", "file2.txt", "dir1", "dir2"]


# create some files in output_dir, to test decompressDir overwrite
for i in range(2):
    with open(os.path.join(output_dir, "file"+str(i)+".txt"), "w") as f:
        f.write("Hello world from output file!!!")
# create some dirs in output_dir, to test decompressDir overwrite
for i in range(2):
    os.mkdir(os.path.join(output_dir, "dir"+str(i)))
    with open(os.path.join(output_dir, "dir"+str(i), "file"+str(i)+".txt"), "w") as f:
        f.write("Hello world from output dir!!!")

compressSelected(root_dir, selected, output_file)
decompressDir(output_file, output_dir)


# test compress empty
output_file = os.path.join(tmp_dir, "test_empty.zip")
compressSelected(root_dir, [], output_file)
decompressDir(output_file, output_dir)
