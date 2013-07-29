import csv
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input", help="input gslib file name")
parser.add_argument("--output", help="output file name or standar output by default", required=False)
parser.add_argument("--delimiter", help="output delimiter", required=False,default=",")
parser.add_argument("--cols", help="columns number to export or all columns by default",required=False,type=int,nargs='+')
parser.add_argument('--header', help="write columns names to output", action='store_false')

args = parser.parse_args()

def transform(inputStream,outputStream,delimiter=",",header=True,cols=None):
    print  cols
    reader = csv.reader(inputStream, delimiter=" ",skipinitialspace=True)
    writer = csv.writer(outputStream, delimiter=delimiter,skipinitialspace=True)

    #title
    row = reader.next()
    #cols
    row = reader.next()
    ncols = int(row[0].split()[0])
    #column name
    columnNames = []
    for i in range(ncols):
        columnNames += [' '.join(reader.next())]

    if header:
        if cols:
            writer.writerow([x for i,x in enumerate(columnNames) if i in cols])
        else:
            writer.writerow(columnNames)
        
    for row in reader:
        if cols:
            writer.writerow([x for i,x in enumerate(row) if i in cols])
        else:
            writer.writerow(row)

        
inputStream = open(args.input)

if args.output:
    outputStream = open(args.output,"w")
else:
    outputStream = sys.stdout

if __name__ == "__main__":
    transform(inputStream,outputStream,delimiter=args.delimiter,header=args.header,cols=args.cols)
