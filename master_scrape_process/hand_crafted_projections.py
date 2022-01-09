
from os import path


def read_projections(filename):
    to_read = open(filename)

    player_to_proj = {}

    for line in to_read.readlines():
        if not "|" in line:
            continue
        parts = line.split("|")
        name = parts[0]

        try:

            proj = float(parts[1].split(' ')[-1])
            if proj > 3000:
                continue
        except:
            continue

        player_to_proj[name] = proj
        print("{} - {}".format(name, proj))
        # import pdb; pdb.set_trace() 

    return player_to_proj