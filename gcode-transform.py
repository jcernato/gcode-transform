#! /bin/python3
from operator import truediv
import sys
import argparse

parser=argparse.ArgumentParser(
    description='''Mirror gcode files along X or Y axis. if Z is given as axis, gcode is rotated 90° CCW''',
    usage='''mirror_gcode --axis X inputfile outputfile''',
    epilog="""Attention, mirroring paths also flips the cutting direction""")
parser.add_argument('--axis', type=str, default='X', help='X, Y or Z!')
parser.add_argument("-o", "--output", help="Directs the output to a name of your choice")
parser.add_argument('filename', nargs='?', type=str)
args=parser.parse_args()

print(args)

if args.filename == None:
    sys.exit("No input file provided")

flip_coordinate = 'Y'
flip_arc_offset = 'J'
if args.axis == 'Y':
    flip_coordinate = 'X'
    flip_arc_offset = 'I'
rotate: bool = False
if args.axis == 'Z':
    rotate = True

class codeline():
    input: str = ""
    def __init__(self, input):
        self.input = input.strip()
        self.comment = ''
        self.movecommand = False
    def rotate(self):
        if "X" and "Y" in self.parameter:
            tmp = self.parameter['X']
            self.parameter['X'] = self.parameter['Y']
            self.parameter['Y'] = tmp*-1
        if "I" and "J" in self.parameter:
            tmp = self.parameter['I']
            self.parameter['I'] = self.parameter['J']
            self.parameter['J'] = tmp*-1
    def flip(self):
        self.parameter[flip_coordinate] = self.parameter[flip_coordinate]*-1
    def get_data(self):
        if not self.movecommand:
            return(self.input)
        data = ""
        for key, value in self.parameter.items():
            data = data + key + str(value) + ' '
        if not self.comment == '':
            data = data + ';' + self.comment
        return(data.strip())


class g01_line(codeline):
    def __init__(self, input):
        self.movecommand = True
        self.input: str = ""
        self.comment: str = ""
        self.line: str = []
        self.input = input.strip()
        if ';' in self.input:
            tmp = self.input.split(';')
            self.input = tmp[0].strip()
            self.comment = tmp[1]
        self.line = self.input.split(' ')
        self.parameter = {}
        self.parameter[self.line[0][0]] = int(self.line[0][1])
        for item in self.line[1:]:
            self.parameter[item[0]] = float(item[1:])
        if args.axis == "Z":
            self.rotate()
        elif flip_coordinate in self.parameter:
            self.flip()


class g23_line(g01_line):
    def ch_dir(self):
        if self.parameter['G'] == 2:
            self.parameter['G'] = 3
        else:
            self.parameter['G'] = 2
    def flip(self):
        self.ch_dir()
        self.parameter[flip_coordinate] = self.parameter[flip_coordinate]*-1
        self.parameter[flip_arc_offset] = self.parameter[flip_arc_offset]*-1
     
        
infile = open(args.filename, 'r')
# i = 0
lines = []
for line in infile:
    # print(i, end=' ')
    # i+=1
    if line.startswith("G0 ") or line.startswith("G1 "):
        lines.append(g01_line(line))
    elif line.startswith("G2 ") or line.startswith("G3 "):
        lines.append(g23_line(line))
    elif line.startswith("G81"):
        lines.append(g01_line)
    else:
        lines.append(codeline(line))


if args.output == None:
    for object in lines:
        print(object.get_data())
else:
    with open(args.output, 'w') as output:
        for object in lines:
            output.write(object.get_data() + '\n')