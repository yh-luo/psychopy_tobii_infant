a = [[1,'a'], [2,'b'], [3,'c']]
b = map(lambda x: (x[0]-1, x[1]), a)
bl = list(b)
print(bl)
bl.remove((0,'a'))
print(bl)