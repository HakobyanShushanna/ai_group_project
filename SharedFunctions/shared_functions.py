def visible_count(line):
    count = 0
    max_height = 0
    for h in line:
        if h > max_height:
            max_height = h
            count += 1
    return count