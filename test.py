from operator import itemgetter

a = [[1, 3], [2, 1], [4, 2], [3, 5]]

 # Sorts by the second element
a = sorted(a, key=itemgetter(1)) 
for item in a:
    print (item[0])