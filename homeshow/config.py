with open('sources.txt', 'r') as infile:
    sources = [s.strip() for s in infile.readlines()]

thresh = 0.2
min_duration = 1
