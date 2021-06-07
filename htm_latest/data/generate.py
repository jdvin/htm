import csv
import numpy as np
import math

f = lambda x: math.sin(x)

with open('training.csv', 'w') as new_file:
    writer = csv.writer(new_file)
    values = []
    for x in np.arange(0, 600.0, 0.1):
        value = str(f(x))
        value = value.translate({',': None})
        writer.writerow(value)
    
    
with open('training.csv', 'r') as new_file:
    lines = new_file.readlines()

lines = filter(lambda x: not x.isspace(), lines)

with open('training1.csv', 'w') as write_file:
    write_file.write("".join(lines))

# open("training.csv", "w").close()
# fh.write("".join(lines))

    # for value in values:
    #     #writer.writerow(value)
    #     writer.writerow(value.translate({ord(','): None}))