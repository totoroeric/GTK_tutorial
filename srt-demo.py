from srt import parse

with open('/home/eric/Downloads/S01E16.eng.srt') as f:
    read_data = f.read()
    # print(read_data)
    subs = parse(read_data)
    # print(list(subs))
    for sub in subs:
        print(sub)
        print("\n")

