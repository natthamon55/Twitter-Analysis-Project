date1 = '14/03/2021'
date2 = '15/03/2021'
d1 = date1.split('/') #แยกเปน list string
d2 = date2.split('/')

d1[2],d1[0] = d1[0],d1[2] #สลับตำแหน่งใน list เอาตน 2 มาสลับกับแรก
d2[2],d2[0] = d2[0],d2[2] 

        
day1 = '-'.join(d1) #เพิ่มขีด - 
day2 = '-'.join(d2)

print(d1)
print(day1)
print(day2)


