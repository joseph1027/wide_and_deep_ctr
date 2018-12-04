count = [0 for i in range(2000000)]
x = []
y = []
z = []

with open('/home/joseph/文件/all_data_before_prune/train.yzx.txt') as f:
	for line in f:
		one_row_data_arr = line.split()
		for j in range(2,len(one_row_data_arr)):
			a = one_row_data_arr[j].split(":")
			feature_id = int(a[0])
			count[feature_id] +=1
	for i in range(2000000):
		if(count[i]!=0):
			print(i,' : ',count[i])
	print('----------------------------------')

with open('/home/joseph/文件/all_data_before_prune/test.yzx.txt') as k:
	for line in k:
		one_row_data_arr = line.split()
		for j in range(2,len(one_row_data_arr)):
			a = one_row_data_arr[j].split(":")
			feature_id = int(a[0])
			count[feature_id] +=1
	for i in range(2000000):
		if(count[i]!=0):
			print(i,' : ',count[i])

with open('/home/joseph/文件/statistics.txt','a') as w:
	for i in range(2000000):
		w.write(i,':',count[i],'\n')