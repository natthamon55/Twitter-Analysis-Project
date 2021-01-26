def three_sum(array):
  print (array)
  array = sort(array)
  print (array)

  val_list = []

  for i in range(0, len(array)): #(0,6)
  
    j = i + 1 #ใช้เพื่อหาตำแหน่งถัดไปใน array
    k = len(array) - 1 #ไว้ใช้กับ array ตำแหน่งสุดท้าย

    while(j < k):
          
      total = array[i] + array[j] + array[k] #หาผลรวมของเลข 3 ตัว
 
      if total > 0: #ไล่ตำแหน่งจากมากมาน้อยลงเรื่อยๆ
        k -= 1
        continue

      if total == 0:
        Triplet = [array[i], array[j], array[k]]
        val_list.append(Triplet)

      j += 1
  print (val_list)

def sort(array):
    less = []
    equal = []
    greater = []

    if len(array) > 1:
        pivot = array[0]
        for x in array:
            if x < pivot:
                less.append(x)
            if x == pivot:
                equal.append(x)
            if x > pivot:
                greater.append(x)

        return sort(less)+equal+sort(greater)  # ใช้ + รวม list เข้าด้วยกัน
  
    else:  
        return array

three_sum([0,-1,2,-3,1,-2])