import csv
import sys
import argparse
from operator import mul

parser = argparse.ArgumentParser()
parser.add_argument("input", help="input cube row_ascii armadillo file name")
parser.add_argument("--output", help="output file name or standar output by default", required=False)
parser.add_argument("--dimensions", help="columns number to export or all columns by default",required=True,type=int,nargs=3)
parser.add_argument("--origin", help="columns number to export or all columns by default",required=True,type=float,nargs=3)
parser.add_argument("--spacing", help="columns number to export or all columns by default",required=True,type=float,nargs=3)

args = parser.parse_args()


def armadilloCubeToVTK(fin,fout,dimensions,origin,spacing):
    n = reduce(mul, dimensions, 1)    
    
    fout.write("# vtk DataFile Version 3.0\n")
    fout.write("vtk output\n")
    fout.write("ASCII\n")
    fout.write("DATASET STRUCTURED_POINTS\n")
    fout.write("DIMENSIONS {0} {1} {2}\n".format(*dimensions))
    fout.write("ORIGIN {0} {1} {2}\n".format(*origin))
    fout.write("SPACING {0} {1} {2}\n".format(*spacing))
    fout.write("POINT_DATA {0}\n".format(n))
    fout.write("SCALARS data float\n")
    fout.write("LOOKUP_TABLE default\n")
    
    for line in fin:
        fout.write(line)


        
inputStream = open(args.input)

if args.output:
    outputStream = open(args.output,"w")
else:
    outputStream = sys.stdout

if __name__ == "__main__":
    armadilloCubeToVTK(inputStream,outputStream,dimensions=args.dimensions,origin=args.origin,spacing=args.spacing)    
    
