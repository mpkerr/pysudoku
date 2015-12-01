def load_su(filename):
    marking = []
    with open(filename,'r') as file:
        row = 0
        for line in filter(None,map(str.strip,file)):
            column = 0
            for token in line.split():
                if not (token == "_" or token == "0"):
                    marking.append(((row,column), int(token)))
                column += 1

            row += 1

    return tuple(marking)



