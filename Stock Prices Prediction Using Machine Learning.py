#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 20,10
from sklearn.preprocessing import MinMaxScaler
scaler=MinMaxScaler(feature_range=(0,1))


# In[2]:


path=r'C:\Users\rohan\test\NSE.csv'
df=pd.read_csv(path)


# In[3]:


df.head()


# In[4]:


df['Date']=pd.to_datetime(df.Date,format='%Y-%m-%d')
df.index=df['Date']
plt.figure(figsize=(16,8))
plt.plot(df['Close'],label='Close Price History')


# In[5]:


data=df.sort_index(ascending=True,axis=0)
new_data=pd.DataFrame(index=range(0,len(df)),columns=['Date','Close'])
for i in range(0,len(data)):
    new_data['Date'][i]=data['Date'][i]
    new_data['Close'][i]=data['Close'][i]
train=new_data[:987]
valid=new_data[987:]
train.shape, valid.shape        


# In[6]:


preds=[]
for i in range(0,valid.shape[0]):
    a=train['Close'][len(train)-248+i:].sum()+sum(preds)
    b=a/248
    preds.append(b)
rms=np.sqrt(np.mean(np.power((np.array(valid['Close'])-preds),2)))
print(rms)


# In[7]:


valid['Predictions']=0
valid['Predictions']=preds
plt.plot(train['Close'])
plt.plot(valid[['Close','Predictions']])


# In[8]:


from fastai.tabular import  add_datepart
add_datepart(new_data, 'Date')
new_data.drop('Elapsed', axis=1, inplace=True)


# In[9]:


new_data['mon_fri'] = 0
for i in range(0,len(new_data)):
    if (new_data['Dayofweek'][i] == 0 or new_data['Dayofweek'][i] == 4):
        new_data['mon_fri'][i] = 1
    else:
        new_data['mon_fri'][i] = 0


# In[10]:


train=new_data[:987]
valid=new_data[987:]
x_train=train.drop('Close',axis=1)
y_train=train['Close']
x_valid=valid.drop('Close',axis=1)
y_valid=valid['Close']
from sklearn.linear_model import LinearRegression
model=LinearRegression()
model.fit(x_train,y_train)


# In[11]:


preds=model.predict(x_valid)
rms=np.sqrt(np.mean(np.power((np.array(y_valid)-np.array(preds)),2)))
rms


# In[12]:


valid['Predictions']=0
valid['Predictions']=preds
valid.index=new_data[987:].index
train.index=new_data[:987].index
plt.plot(train['Close'])
plt.plot(valid[['Close','Predictions']])


# In[13]:


from sklearn import neighbors
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler
scaler=MinMaxScaler(feature_range=(0,1))


# In[14]:


x_train_scaled=scaler.fit_transform(x_train)
x_train=pd.DataFrame(x_train_scaled)
x_valid_scaled=scaler.fit_transform(x_valid)
x_valid=pd.DataFrame(x_valid_scaled)


params={'n_neighbors':[2,3,4,5,6,7,8,9]}
knn=neighbors.KNeighborsRegressor()
model=GridSearchCV(knn,params,cv=5)


model.fit(x_train,y_train)
preds=model.predict(x_valid)


# In[15]:


rms=np.sqrt(np.mean(np.power((np.array(y_valid)-np.array(preds)),2)))
rms


# In[16]:


valid['Predictions'] = 0
valid['Predictions'] = preds
plt.plot(valid[['Close', 'Predictions']])
plt.plot(train['Close'])


# In[17]:


import numpy as np
from pmdarima.arima import auto_arima


# In[18]:


data=df.sort_index(ascending=True, axis=0)
train=data[:987]
valid=data[987:]
training=train['Close']
validation=valid['Close']
model=auto_arima(training,start_p=1,start_q=1,max_p=1,max_q=3,m=12,start_P=0,seasonal=True,d=1,D=1,trace=True,error_action='ignore',suppress_warnings=True)
model.fit(training)
forecast=model.predict(n_periods=248)
forecast=pd.DataFrame(forecast,index=valid.index,columns=['Prediction'])
rms=np.sqrt(np.mean(np.power((np.array(valid['Close'])-np.array(forecast['Prediction'])),2)))
rms

plt.plot(train['Close'])
plt.plot(valid['Close'])
plt.plot(forecast['Prediction'])


# In[31]:


from fbprophet import Prophet
new_data=pd.DataFrame(index=range(0,len(df)),columns=['Date','Close'])
for i in range(0,len(data)):
    new_data['Date'][i] = data['Date'][i]
    new_data['Close'][i] = data['Close'][i]

new_data['Date'] = pd.to_datetime(new_data.Date,format='%Y-%m-%d')
new_data.index = new_data['Date']

#preparing data
new_data.rename(columns={'Close': 'y', 'Date': 'ds'}, inplace=True)

#train and validation
train = new_data[:987]
valid = new_data[987:]
model=Prophet()
model.fit(train)
close_prices=model.make_future_dataframe(periods=len(valid))
forecast=model.predict(close_prices)
forecast_valid=forecast['yhat'][987:]
rms=np.sqrt(np.mean(np.power((np.array(valid['y'])-np.array(forecast_valid)),2)))
rms

valid['Predictions'] = 0
valid['Predictions'] = forecast_valid.values

plt.plot(train['y'])
plt.plot(valid[['y', 'Predictions']])


# In[30]:


from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout,LSTM

data=df.sort_index(ascending=True,axis=0)
new_data = pd.DataFrame(index=range(0,len(df)),columns=['Date', 'Close'])
for i in range(0,len(data)):
    new_data['Date'][i] = data['Date'][i]
    new_data['Close'][i] = data['Close'][i]

#setting index
new_data.index = new_data.Date
new_data.drop('Date', axis=1, inplace=True)

#creating train and test sets
dataset = new_data.values

train = dataset[0:987,:]
valid = dataset[987:,:]

scaler=MinMaxScaler(feature_range=(0,1))
scaled_data=scaler.fit_transform(dataset)
x_train, y_train=[],[]
for i in range(60,len(train)):
    x_train.append(scaled_data[i-60:i,0])
    y_train.append(scaled_data[i,0])

x_train, y_train=np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

model=Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1)))
model.add(LSTM(units=50))
model.add(Dense(1))
model.compile(loss='mean_squared_error',optimizer='adam')
model.fit(x_train,y_train,epochs=1,batch_size=1,verbose=2)
inputs=new_data[len(new_data)-len(valid)-60:].values
inputs=inputs.reshape(-1,1)
inputs=scaler.transform(inputs)
X_test=[]
for i in range(60,inputs.shape[0]):
    X_test.append(inputs[i-60:i,0])
X_test=np.array(X_test)
X_test=np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))
closing_price=model.predict(X_test)
closing_price=scaler.inverse_transform(closing_price)



rms=np.sqrt(np.mean(np.power((valid-closing_price),2)))
rms



train = new_data[:987]
valid = new_data[987:]
valid['Predictions'] = closing_price
plt.plot(train['Close'])
plt.plot(valid[['Close','Predictions']])


# In[ ]:




