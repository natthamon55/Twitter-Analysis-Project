#ผสมสิบ รวมกันได้ 10 มีกี่ชุด
list_row = [[1, 3, 5, 7], 
            [2, 4, 8, 2], 
            [6, 3, 1, 1], 
            [2, 3, 5, 6]]
row1,row2,row3,row4 = [1, 3, 5, 7], [2, 4, 8, 2], [6, 3, 1, 1], [2, 3, 5, 6]
column1,column2,column3,column4 = [],[],[],[]

for i in list_row :
    column1.append(i[0])

for i in list_row:
    column2.append(i[1])

for i in list_row :
    column3.append(i[2])

for i in list_row :
    column4.append(i[3])
#---------------------------------------------------------#
def count_10(n) :
    count = 0
    if sum(n) == 10 :
        count += 1
    elif sum(n) > 10 :
        n.pop()
        if sum(n) == 10 :
            count += 1
        elif sum(n) > 10 :
            n.pop()
            if sum(n) == 10 :
                count += 1
            
    return count 

#-------row-------#
r1 = count_10(row1)
r2 = count_10(row2)
r3 = count_10(row3)
r4 = count_10(row4)

#-------column-----#
c1 = count_10(column1)
c2 = count_10(column2)
c3 = count_10(column3)
c4 = count_10(column4)

#---------- กี่ชุด------------#
total = r1 + r2 + r3 + r4 + c1 + c2 + c3 + c4
print(total)



