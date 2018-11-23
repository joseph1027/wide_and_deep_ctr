from scipy.sparse import *
from scipy import *
import numpy as np
import keras
from keras.models import Sequential,Model
from keras.layers import Input,Embedding,Dense,Dropout,Activation,Add,concatenate
from keras import optimizers
from sklearn.utils import class_weight,compute_class_weight,shuffle
from keras.activations import relu
from keras import regularizers
from keras.callbacks import EarlyStopping,Callback
import random
from sklearn.metrics import roc_auc_score

batch_size = 102400
data_size = 10000000

def read_train_data(f,batch_size):
	x=[]
	y=[]
	z=[]
	sm = []
	for i in range(batch_size):
		one_row_data = f.readline()
		one_row_data_arr = one_row_data.split()
		y.append(one_row_data_arr[0])
		z.append(one_row_data_arr[1])
		feature_list=[]
		for j in range(2,len(one_row_data_arr)):
			a = one_row_data_arr[j].split(":")
			feature_id = int(a[0])
			feature_list.append(feature_id)
		x.append(feature_list)
	sm = to_sparse(x,z)
	y_ca = keras.utils.to_categorical(y,2)
	#global cw
	#cw = compute_weight(y_ca)
	return sm,y_ca

def read_test_data():
	y_test = []
	z_test = []
	x_test = []
	with open('/home/joseph/文件/all_data_before_prune/test_label_0.txt') as ff:
		#due to unbalanced label of click, we want more label "1"! select them out!
		for i in range(50000):
			one_row_data = ff.readline()
			#one_row_data = line
			one_row_data_arr = one_row_data.split()
			y_test.append(one_row_data_arr[0])
			z_test.append(one_row_data_arr[1])
			feature_list=[]
			for j in range(2,len(one_row_data_arr)):
				a = one_row_data_arr[j].split(":")
				feature_id = int(a[0])
				feature_list.append(feature_id)
			x_test.append(feature_list)
		#Then read another half of data, most of them are "0"!
	with open('/home/joseph/文件/all_data_before_prune/test_label_1.txt') as ff:
		for k in range(50000):
			one_row_data = ff.readline()
			one_row_data_arr = one_row_data.split()
			y_test.append(one_row_data_arr[0])
			z_test.append(one_row_data_arr[1])
			feature_list=[]
			for j in range(2,len(one_row_data_arr)):
				a = one_row_data_arr[j].split(":")
				feature_id = int(a[0])
				feature_list.append(feature_id)
			x_test.append(feature_list)
	sm_test = to_sparse(x_test,z_test)
	y_test_ca = keras.utils.to_categorical(y_test,2)
	return sm_test,y_test_ca,y_test

def to_sparse(f_id,z_label):
	row=[]
	col=[]
	val=[]
	row_cnt = 0
	for r in f_id:
		for e in r:
			row.append(row_cnt)
			col.append(e)
			val.append(1)
		row.append(row_cnt)	
		col.append(1999999)
		val.append(int(z_label[row_cnt]))
		row_cnt +=1
	sparse_matrix = csr_matrix((val,(row,col)),shape=(max(row)+1,max(col)+1))
	return sparse_matrix

def get_model():
	input1 = Input(batch_shape =(None,2000000),sparse = True)
	#hidden = Dense(32,activation='relu')(input1)
	out = Dense(2,activation = 'softmax',kernel_initializer='zeros')(input1)#,W_regularizer=regularizers.l2(0.002)
	model = Model(inputs=input1, outputs = out)
	adam = keras.optimizers.Adam(lr=0.00001,beta_1=0.9,beta_2=0.999,epsilon=1e-08, decay=0.0)
	model.compile(loss = 'categorical_crossentropy', optimizer=adam, metrics=['accuracy'])
	model.summary()
	return model

def mygenerator(batch_size,data_size):
	accumulation=0
	while True:
		with open('/home/joseph/文件/all_data_before_prune/train.yzx.txt') as f:
			if((accumulation+batch_size)<data_size):
				sm,y_ca=read_train_data(f,batch_size)
				accumulation += batch_size
			else:
				sm,y_ca=read_train_data(f,data_size-accumulation)
				accumulation = 0
			yield sm,y_ca

class roc_callback(Callback):
    def __init__(self,testing_data):
        self.x_val = testing_data[0]
        self.y_val = testing_data[1]

    def on_train_begin(self, logs={}):
        return

    def on_train_end(self, logs={}):
        return

    def on_epoch_begin(self, epoch, logs={}):
        return

    def on_epoch_end(self, epoch, logs={}):
        y_pred_val = self.model.predict(self.x_val)
        #print(y_pred_val)
        roc_val = roc_auc_score(self.y_val, y_pred_val)
        print(('roc-auc_val:'+str(round(roc_val,4))),end=100*' '+'\n')
        return

    def on_batch_begin(self, batch, logs={}):
        return

    def on_batch_end(self, batch, logs={}):
        return

def compute_weight(data_size):
	yy = []
	with open('/home/joseph/文件/all_data_before_prune/train.yzx.txt') as t:
		for i in range(data_size):
			line_data = t.readline().split()
			yy.append(line_data[0])
	yy = keras.utils.to_categorical(yy,2)
	y_integers = np.argmax(yy, axis=1)
	class_weights = compute_class_weight('balanced', np.unique(y_integers), y_integers)
	d_class_weights = dict(enumerate(class_weights))
	return d_class_weights

if __name__ == "__main__":
	sm_test,y_test_ca,y_test = read_test_data()
	model = get_model()
	early_stopping = EarlyStopping(monitor='val_loss', patience=0, verbose=1, mode='auto')
	cw = compute_weight(data_size)
	history = model.fit_generator(mygenerator(batch_size,data_size),steps_per_epoch=int(data_size/batch_size)+1,epochs=1000,verbose=1,validation_data=(sm_test,y_test_ca),class_weight=cw,callbacks=[roc_callback(testing_data=(sm_test,y_test_ca)),early_stopping],shuffle=True)
	print(cw)
	ynew = model.predict(sm_test)
	tp=0
	tn=0
	fp=0
	fn=0
	for i in range(len(y_test)):
		if(ynew[i][0]>ynew[i][1] and y_test[i]=="0"):
			tn +=1
		elif(ynew[i][0]>ynew[i][1] and y_test[i]=="1"):
			fn +=1
		elif(ynew[i][0]<ynew[i][1] and y_test[i]=="0"):
			fp +=1
		elif(ynew[i][0]<ynew[i][1] and y_test[i]=="1"):
			tp +=1
	print("True Negative :",tn)
	print("True Positive :",tp)
	print("False Negative :",fn)
	print("False Positive :",fp)