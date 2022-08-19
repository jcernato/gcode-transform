#! /bin/python3
import sys
import argparse

parser=argparse.ArgumentParser(
    description='''Mirror gcode files along X or Y axis. ''',
    usage='''mirror_gcode --axis X inputfile outputfile''',
    epilog="""Attention, mirroring paths also flips the cutting direction""")
parser.add_argument('--axis', type=str, default='X', help='X or Y!')
parser.add_argument("-o", "--output", help="Directs the output to a name of your choice")
parser.add_argument('filename', nargs='?', type=str)
args=parser.parse_args()

print(args)

if args.filename == None:
    sys.exit("No input file provided")

if args.output == None:
    sys.exit("No output path provided")


flip_coordinate = 'Y'
flip_arc_offset = 'J'
if args.axis == 'Y':
    flip_coordinate = 'X'
    flip_arc_offset = 'I'

infile = open(args.filename, 'r')
with open(args.output, 'w') as output:
    for linenl in infile:
        line = linenl.strip()
        if line.startswith('G0') or line.startswith('G1'):
            items = line.split(' ')
            for item in items:
                if item.startswith(flip_coordinate):
                    value = float(item[1:])
                    # print(flip_coordinate + str(value*(-1)), end=' ')
                    output.write(flip_coordinate + str(value*(-1)) + ' ')
                else:
                    #  print(item, end=' ')
                     output.write(item + ' ')

        elif line.startswith('G2') or line.startswith('G3'):
            items = line.split(' ')
            for item in items:
                if item.startswith('G2'):
                    # print("G3", end=' ')
                    output.write("G3 ")
                elif item.startswith('G3'):
                    # print("G2", end=' ')
                    output.write("G2 ")
                elif item.startswith(flip_coordinate):
                    value = float(item[1:])
                    # print(flip_coordinate + str(value*(-1)), end=' ')
                    output.write(flip_coordinate + str(value*(-1)) + ' ')
                elif item.startswith(flip_arc_offset):
                    value = float(item[1:])
                    # print(flip_arc_offset + str(value*(-1)), end=' ')
                    output.write(flip_arc_offset + str(value*(-1)) + ' ')
                else:
                    #  print(item, end=' ')
                     output.write(item + ' ')

        else:
            # print(line, end='')
            output.write(line)
        output.write('\n')