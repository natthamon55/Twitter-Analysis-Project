print('number of lines :')
n = int(input())
def maxRegions(n): 
    num = n * (n + 1) // 2 + 1
    print("number of divide area :" +str(num))  

maxRegions(n) 