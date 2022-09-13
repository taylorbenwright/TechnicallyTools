import math
import decimal


def subtract_z():
    with open('UEEnv/CurveFile.txt', mode='r+') as f:
        lines = f.readlines()
        for ind, line in enumerate(lines):
            splits = line.split('OutputValue=')
            if len(splits) == 1:
                continue
            value = decimal.Decimal(splits[1].rstrip(')\n'))
            value *= decimal.Decimal(-1.0)
            new_line = splits[0] + 'OutputValue=' + str(value) + ')\n'
            lines[ind] = new_line
        f.seek(0)
        f.writelines(lines)
        f.truncate()


subtract_z()
