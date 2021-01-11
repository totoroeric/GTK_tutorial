from srt import parse

with open('/home/eric/Downloads/S01E22.eng.srt') as f:
    read_data = f.read()
    # print(read_data)
    subs = parse(read_data)
    # print(list(subs))
    for sub in subs:
        print("index: ", sub.index)
        print("start: ", sub.start)
        print("end: ", sub.end)
        print("content: ", sub.content)
        print("\n")

