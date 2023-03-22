graph = {
    "H" : {"W":0.64, "P":1.34, "S":1.98, "H":1},
    "S" : {"P":0.67, "W":0.31, "H":0.48},
    "W" : {"P":1.95, "S":3.1, "H":1.49},
    "P" : {"W":0.5, "S":1.45, "H":0.75},
}
print(graph)

res = {}
todo = [("H", 1)]
while len(todo) != 0:
    curr, capital = todo.pop(0)
    if len(curr) == 5:
        cap = capital * graph[curr[-1]]['H']
        res[curr] = cap
        continue
    for newgood in graph[curr[-1]]:
        rate = graph[curr[-1]][newgood]
        route = curr + newgood
        newcap = capital * rate
        todo.append((route, newcap))

sorted_res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1])}
print(sorted_res)
print(len(sorted_res))