# coding:utf-8


import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import statsmodels.api as sm 
import sys

from statsmodels.graphics.api import qqplot  #用来作QQ图
from statsmodels.tsa.stattools import adfuller #ADF单位根检验
from statsmodels.tsa.stattools import acf,pacf #自相关，偏自相关
from statsmodels.tsa.arima_model import ARMA  #ARIMA处理
from statsmodels.tsa.seasonal import seasonal_decompose #用来季节性分解处理
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf#用来做自相关，偏自相关图
from scipy import stats
from pandas import Series,DataFrame

plt.rcParams['font.sans-serif'] = ['SimHei']  #用来显示中文
plt.rcParams['axes.unicode_minus'] = False  #用来正常显示负号


class ARMAModelTest:
	'''
	基于ARIMA模型，对时间序列做平稳化处理，利用差分查找最佳d值，
	根据平稳化处理后的时间序列自相关、偏自相关图选择合适的p,q值，
	对ARMA模型进行AIC、BIC、HQIC准则验证，
	检查残差序列：分别用自相关、偏自相关图，D-W检验，正态分布检验，qq图检验，Ljung-Box
	检验，
	对接下来的走势进行预测。
	'''

	def __init__(self,time,num=100,lags=40):
		self.time = time
		self.num = num
		self.lags = lags

	#第一步：对时间序列做平稳化处理（一般使用差分）
	def ser_stable_plot(self,timeSer,target='Latestprice',diff=1):
		global data 
		data = timeSer.ix[self.time][target][:self.num].diff(diff)
		data.index = pd.date_range(data.index[0],periods=len(data))
		data.plot(use_index=False,figsize=(12,6),linewidth=2,grid=True)
		plt.title(u'一阶差分平稳化处理后')
		plt.show()
		#print data

	#第二步：选择合适的p,q
	def p_q_choice(self,timeSer):
		#fig1 = sm.graphics.tsa.plot_acf(data,lags=lags,ax=ax[0])
		#fig2 = sm.graphics.tsa.plot_pacf(data,lags=lags,ax=ax[1])
		timeSer = timeSer.ix[self.time]
		timeSer.index = pd.date_range(timeSer.index[0],periods=len(timeSer))
		figure001 = plt.figure(figsize=(12,6))	
		ax1 = figure001.add_subplot(211)
		ax2 = figure001.add_subplot(212)	
		fig1 = plot_acf(timeSer[:self.num].diff(1).dropna(),lags=self.lags,ax=ax1)
		fig2 = plot_pacf(timeSer[:self.num].diff(1).dropna(),lags=self.lags,ax=ax2)
		plt.show()	


########################################################

	def proper_model(self,timeSer):
	    global p
	    global q

	    timeSerDiff = timeSer[:self.num].diff(1).dropna()
	    acf_x,confint = acf(timeSerDiff,nlags=self.lags,alpha=0.05)
	    acf_px,confint2 = pacf(timeSerDiff,nlags=self.lags,alpha=0.05)
	    print 'confint',confint
	    print 'acf_x',acf_x
	    confint = confint - confint.mean(1)[:,None]
	    confint2 = confint2 - confint2.mean(1)[:,None]
	    #pArray = acf(timeSerDiff,nlags=self.lags)
	    #qArray = pacf(timeSerDiff,nlags=self.lags)
	    #pq_range_small = -1.96/np.sqrt(len(timeSerDiff))
	    #pq_range_big = 1.96/np.sqrt(len(timeSerDiff))
	    for key1, x, y, z in zip(range(self.lags),acf_x,confint[:,0],confint[:,1]):
	    	if x > y and x < z:
	    		q = key1
	    		print q
	    		break

	    for key2, x, y, z in zip(range(self.lags),acf_px,confint2[:,0],confint2[:,1]):
	    	if x > y and x < z:
	    		p = key2
	    		print 'p'
	    		break

	    print 'p',p,'\n','q',q
	# def proper_model(self,timeSer):
	# 	global p
	# 	global q 
	# 	init_aic = sys.maxint
	# 	init_p = 0
	# 	init_q = 0
	# 	init_properModel = None
	# 	for p in np.arange(1,self.lags):
	# 		for q in np.arange(1,self.lags):
	# 			model = ARMA(timeSer,order=(p,q))
	# 			try:
	# 				results_ARMA = model.fit()#disp=-1,method='css')
	# 			except:
	# 				continue
	# 			bic = results_ARMA.bic 
	# 			if aic < init_aic:
	# 				init_p = p
	# 				init_q = q 
	# 				init_properModel = results_ARMA
	# 				init_aic = aic 	
	# 				print init_p
	# 				print init_q	
	# 	p = init_p 
	# 	q = init_q
		#return init_aic,init_p,init_q,init_properModel
################################################################

	#第三步：采用ARMA模型的AIC法则
	#def arma_mod(self,timeSer):
	def arma_mod(self,p,q,timeSer):#手动选择p,q值
		#arma_mod = sm.tsa.ARMA(data,order=p_q_choice(lags)).fit()
		global ar_mod
		global ma_mod 
		global arma_mod

		timeSer = timeSer.ix[self.time]
		timeSer.index = pd.date_range(timeSer.index[0],periods=len(timeSer)) 

		ar_mod = ARMA(timeSer[:self.num],order=(p,0)).fit()
		print u'-----------AR模型-----------'
		print 'AIC: ',ar_mod.aic 
		print 'BIC: ',ar_mod.bic 
		print 'HQIC: ',ar_mod.hqic 
		ma_mod = ARMA(timeSer[:self.num],order=(0,q)).fit()
		print u'-----------MA模型-----------'
		print 'AIC: ',ma_mod.aic 
		print 'BIC: ',ma_mod.bic 
		print 'HQIC: ',ma_mod.hqic 
		arma_mod = ARMA(timeSer[:self.num],order=(p,q)).fit()
		print u'-----------ARMA模型-----------'
		print 'AIC: ',arma_mod.aic 
		print 'BIC: ',arma_mod.bic 
		print 'HQIC: ',arma_mod.hqic 

	#第四步：ADF单位根检验，检查残差序列，D-W（德宾-沃森)检验
	def check_rasid_DW(self):
		print 'check_rasid_DW'

		ar_resid = adfuller(ar_mod.resid)
		ma_resid = adfuller(ma_mod.resid)
		arma_resid = adfuller(arma_mod.resid)

		df1 = Series(ar_resid[0:4],index=['Test Statistic','p-value','Lags Used','Nob'])
		for key, value in ar_resid[4].items():
			df1['Critical Value(%s)'%key] = value 

		df2 = Series(ma_resid[0:4],index=['Test Statistic','p-value','Lags Used','Nob'])
		for key,value in ma_resid[4].items():
			df2['Critical Value(%s)'%key] = value 

		df3 = Series(arma_resid[0:4],index=['Test Statistic','p-value','Lags Used','Nob'])
		for key,value in arma_resid[4].items():
			df3['Critical Value(%s)'%key] = value 

		df = pd.concat([df1,df2,df3],axis=1,keys=['ar_resid','ma_resid','arma_resid'])
		print df 

		figure002 = plt.figure(figsize=(12,6))	
		ax3 = figure002.add_subplot(211)
		ax4 = figure002.add_subplot(212)
		fig3 = plot_acf(arma_mod.resid,lags=self.lags,ax=ax3)
		fig4 = plot_pacf(arma_mod.resid,lags=self.lags,ax=ax4)
		plt.show()
		#第五步：D-W（德宾-沃森)检验
		dw = sm.stats.durbin_watson(arma_mod.resid.values)
		print 'D-W: ',dw


	#第六步：对残差做正态分布检验
	def check_norm_qq(self,):
		norm = stats.normaltest(arma_mod.resid)
		print norm 

		figure003 = plt.figure(figsize=(12,6))	
		ax5 = figure003.add_subplot(111)		
		figqq = qqplot(arma_mod.resid,ax=ax5,fit=True,line='q')
		plt.show()

	#第七步：残差Ljung-Box检验（Q检验）
	def check_q(self,):
		r,q,p = sm.tsa.acf(arma_mod.resid,qstat=True)
		df = np.c_[range(1,41),r[1:],q,p]
		frame = DataFrame(df,columns=['Lags','ACF','Q','Prob(>Q)'])
		frame.set_index('Lags')
		pct = len(frame[frame['Prob(>Q)']>0.05])/len(frame)
		print 'pct',pct

	#第八步：预测
	def predict_target(self,timeSer,start=None,end=None,dynamic=False):
		#timeSer.index = pd.date_range(timeSer.index[0],periods=len(timeSer))
		timeSer2 = timeSer.ix[self.time]
		timeSer2.index = pd.date_range(timeSer2.index[0],periods=len(timeSer2))
		timeSer_handle = timeSer2.ix[:self.num]
		timeSer_handle.index = pd.date_range(timeSer_handle.index[0],periods=len(timeSer_handle))
		#print timeSer_handle
		predict_target = arma_mod.predict(start=start,end=end,dynamic=dynamic)
		print predict_target 
		figure004 = plt.figure(figsize=(12,6*3))	
		ax6 = figure004.add_subplot(311)
		ax7 = figure004.add_subplot(312)
		ax8 = figure004.add_subplot(313)
		timeSer2.plot(ax=ax6,lw=2.5,color='red')
		timeSer2.plot(ax=ax7,lw=2.5,color='red')	
		timeSer2.plot(ax=ax8,lw=2.5,color='red')		
		timeSer_handle.plot(ax=ax6,lw=2)
		timeSer_handle.plot(ax=ax7,lw=2)	
		timeSer_handle.plot(ax=ax8,lw=2)			
		arma_mod.plot_predict(start,end,dynamic=dynamic,ax=ax6,plot_insample=False)
		ax6.set_title(u'使用ARMA模型预测')
		ar_mod.plot_predict(start,end,dynamic=dynamic,ax=ax7,plot_insample=False)
		ax7.set_title(u'使用AR模型预测')
		ma_mod.plot_predict(start,end,dynamic=dynamic,ax=ax8,plot_insample=False)
		ax8.set_title(u'使用MA模型预测')
		#return figs1,figs2
		plt.show()
		

if __name__ == '__main__':
	dataNeed = pd.read_csv('dataFortime.csv')
	dataNeed2 = dataNeed.ix[:,1:3].set_index('Time')
	dataNeed3 = dataNeed.ix[:,1:3].set_index('Time')
	dataNeed3.index = pd.to_datetime(dataNeed3.index)
	dataNeed3.index = dataNeed3.index.map(lambda x:x.strftime('%Y-%m-%d'))
	dataNeed3.index = pd.to_datetime(dataNeed3.index)

	dataNeed2.index = pd.to_datetime(dataNeed2.index)
	dataNeed2.index = dataNeed2.index.map(lambda x:x.strftime('%Y-%m-%d'))
	dataNeed2.index = pd.to_datetime(dataNeed2.index)
	timeRight = dataNeed2.index.unique()
	print u'有记录日期为： ',timeRight

	time = raw_input(unicode('请输入你要预测的日期: ','utf-8').encode('gbk'))
	while time not in timeRight:
		print u'你输入的时间不在记录日期内，请重新输入!'
		time = raw_input(unicode('请输入你要预测的日期: ','utf-8').encode('gbk'))

	test = ARMAModelTest(time=time,num=100,lags=40)
	test.ser_stable_plot(dataNeed2,target='Latestprice',diff=1)
	test.p_q_choice(dataNeed2)
	# p = input(unicode('请根据自相关图输入对应的p: ','utf-8').encode('gbk'))
	# q = input(unicode('请根据自相关图输入对应的q: ','utf-8').encode('gbk'))
	test.proper_model(dataNeed2)
	test.arma_mod(p,q,dataNeed2)
	test.check_rasid_DW()
	test.check_norm_qq()
	test.check_q()

	dataNeed3 = dataNeed3.ix[time][:100]
	dataNeed3.index = pd.date_range((str(dataNeed3.index[0])[:10]),periods=len(dataNeed3))

	print u'转换后实际结束日期为： ',str(dataNeed3.index[99])

	end = False
	while not end:
		
		start = raw_input(unicode('请输入转换后的预测起始时间： ','utf-8').encode('gbk'))
		end = raw_input(unicode('请输入转换后的预测结束时间： ','utf-8').encode('gbk'))
		certain = raw_input(unicode('请输入是否加入已有数据的验证：（yes/no)','utf-8').encode('gbk'))
		if certain.strip() == 'yes':
			dynamic = False
		else:
			dynamic = True 
		try:
			test.predict_target(dataNeed2,start=start,end=end,dynamic=dynamic)
		except:
			print u'数据输入有误！'
		panduan = raw_input(unicode('是否结束预测：（yes/no)','utf-8').encode('gbk'))
		if panduan.strip() == 'yes':
			end = True
		else:
			end = False




