#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
# import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn import metrics
import pickle
import warnings
warnings.filterwarnings("ignore")


# In[2]:


data = pd.read_csv(r'D:\Project\archive\train.csv')
data.head()


# In[3]:


# Checking number of data point(rows) & number of features(columns)

data.shape


# In[4]:


# Getting some information about dataset

data.info()


# In[5]:


# Checking sum of missing values

data.isnull().sum()


# In[6]:


# Finding Mean value of 'Item_Weight' column as it's a numerical column

data['Item_Weight'].mean()


# In[7]:


# Filling missing value in 'Item_Weight' column with its mean value

data['Item_Weight'].fillna(data['Item_Weight'].mean(), inplace=True)


# In[8]:


# Checking sum of missing values for 'Item_Weight' column

data.isnull().sum()


# In[9]:


mode_of_outlet_size = data.pivot_table(values='Outlet_Size', columns='Outlet_Type', aggfunc=(lambda x: x.mode()[0]))


# In[10]:


print(mode_of_outlet_size)


# In[11]:


missing_values = data['Outlet_Size'].isnull()
print(missing_values)


# In[12]:


data.loc[missing_values, 'Outlet_Size'] = data.loc[missing_values, 'Outlet_Type'].apply(lambda x: mode_of_outlet_size)


# In[13]:


data.isnull().sum()


# In[14]:


data.describe()


# In[15]:


sns.set()

# it will give us some themes for our plots


# In[16]:


plt.figure(figsize=(6, 6))
sns.distplot(data['Item_Weight'])
plt.title('Distribution of Item_Weight Feature')
plt.show()


# In[17]:


plt.figure(figsize=(6, 6))
sns.distplot(data['Item_Visibility'])
plt.title('Distribution of Item_Visibility Feature')
plt.show()


# In[18]:


# Item_MRP column distribution

plt.figure(figsize=(6, 6))
sns.distplot(data['Item_MRP'])
plt.title('Distribution of Item_MRP Feature')
plt.show()


# In[19]:


plt.figure(figsize=(6, 6))
sns.distplot(data['Item_Outlet_Sales'])
plt.title('Distribution of Item_Outlet_Sales Feature')
plt.show()


# In[20]:


plt.figure(figsize=(6, 6))
sns.countplot(x='Outlet_Establishment_Year', data=data)
plt.title('Count of Outlet_Establishment_Year column')
plt.show()


# In[21]:


# Count of Item_Fat_Content column

plt.figure(figsize=(6, 6))
sns.countplot(x='Item_Fat_Content', data=data)
plt.title('Count of Item_Fat_Content column')
plt.show()


# In[22]:


# Count of Item_Type column

plt.figure(figsize=(30, 6))
sns.countplot(x='Item_Type', data=data)
plt.title('Count of Item_Type column')
plt.show()


# In[23]:


# Count of Outlet_Location_Type column

plt.figure(figsize=(6, 6))
sns.countplot(x='Outlet_Location_Type', data=data)
plt.title('Count of Outlet_Location_Type column')
plt.show()


# In[24]:


# Count of Outlet_Type column

plt.figure(figsize=(10, 6))
sns.countplot(x='Outlet_Type', data=data)
plt.title('Count of Outlet_Type column')
plt.show()


# In[25]:


data.head()


# In[26]:


data['Item_Fat_Content'].value_counts()


# In[27]:


data.replace({'Item_Fat_Content': {'low fat': 'Low Fat', 'LF': 'Low Fat', 'reg': 'Regular'}}, inplace=True)


# In[28]:


data['Item_Fat_Content'].value_counts()


# In[29]:


encoder = LabelEncoder()


# In[30]:


data['Item_Identifier'] = encoder.fit_transform(data['Item_Identifier'])
data['Item_Fat_Content'] = encoder.fit_transform(data['Item_Fat_Content'])
data['Item_Type'] = encoder.fit_transform(data['Item_Type'])
data['Outlet_Identifier'] = encoder.fit_transform(data['Outlet_Identifier'])
data['Outlet_Size'] = encoder.fit_transform(data['Outlet_Size'].astype(str))
data['Outlet_Location_Type'] = encoder.fit_transform(data['Outlet_Location_Type'])
data['Outlet_Type'] = encoder.fit_transform(data['Outlet_Type'])


# In[31]:


data.head()


# In[32]:


x = data.drop(columns='Item_Outlet_Sales', axis=1)
y = data['Item_Outlet_Sales']


# In[33]:


print(x)


# In[34]:


print(y)


# In[35]:


x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=2)


# In[36]:


print(x.shape, x_train.shape, x_test.shape, y_train.shape, y_test.shape)


# In[37]:


reg = XGBRegressor()


# In[38]:


reg.fit(x_train, y_train)


# In[39]:


train_data_predict = reg.predict(x_train)


# In[40]:


r2_train = metrics.r2_score(y_train, train_data_predict)
print('R Squared Value :', r2_train)


# In[41]:


test_data_predict = reg.predict(x_test)


# In[42]:


r2_test = metrics.r2_score(y_test, test_data_predict)
print('R Squared Value :', r2_test)


# In[62]:
# In[63]:

pickle.dump(reg, open('model. pkl', 'wb'))


# In[64]:


pickle.load(open('model.pkl', 'rb'))
