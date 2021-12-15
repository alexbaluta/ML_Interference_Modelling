import argparse
import h2o
import numpy as np
import pandas as pd
import time

from h2o.automl import H2OAutoML
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.model_selection import train_test_split

def automl_predict(train, test, max_runtime_secs=3600):
	"""
	Use H2O AutoML to learn a regressor on the train set. 
	Then use the regressor to make predictions on the test set.
	Output evaluation metrics on the test set predictions.

	This follows from the H2O official documentation:
	https://docs.h2o.ai/h2o/latest-stable/h2o-docs/automl.html#code-examples

	Parameters: 
    train (Pandas DataFrame): Train set for regressor.
    test (Pandas DataFrame): Test set for regressor.

    Returns:
    float: MAPE metric
	"""
	true_labels = np.array(test['total_time'])

	test_original = test.copy()

	train = h2o.H2OFrame(train)
	test = h2o.H2OFrame(test)

	x = train.columns
	y = 'total_time'
	x.remove(y)

	aml = H2OAutoML(seed=7, 
		max_runtime_secs=max_runtime_secs, 
		stopping_metric="MAE", 
		sort_metric="MAE")

	aml.train(x=x, y=y, training_frame=train)

	perf = aml.leader.model_performance(test)

	preds = aml.leader.predict(test)
	preds = preds.as_data_frame()
	preds = np.array(preds['predict'].tolist())

	mape = mean_absolute_percentage_error(true_labels, preds)

	return mape

def linear_regr_predict(train, test):
	"""
	Use linear regression to learn a regressor on the input train set. 
	Then use the regressor to make predictions on the test set.
	Output evaluation metrics on the test set predictions.

	Parameters: 
    train (Pandas DataFrame): Train set for classifier.
    test (Pandas DataFrame): Test set for classifier.

    Returns:
    float: MAPE metric
	"""

	train_y = train['total_time']
	train_X = train.drop(columns=['total_time'])
	
	true_labels = np.array(test['total_time'])
	test_X = test.drop(columns=['total_time'])

	regr = LinearRegression().fit(train_X, train_y)
	preds = regr.predict(test_X)

	mape = mean_absolute_percentage_error(true_labels, preds)

	return mape

def select_data_subset(df):
	vm_cols_1vm = ['host_cpu', 'host_mem']
	vm_cols_2vm = ['web_host_cpu', 'web_host_mem', 'db_host_cpu', 'db_host_mem']
	container_cols = ['acme_web_cpu', 'acme_web_mem', 'acme_db_cpu', 'acme_db_mem']
	app_cols = ['request_rate']
	target_col = ['total_time']
	other_col = ['httperf_num', 'httperf_per']

	if 'web_host_cpu' in df.columns:
		cols = vm_cols_2vm
	else:
		cols = vm_cols_1vm

	cols = cols + container_cols + app_cols + target_col + other_col
	return df[cols]

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-D", "--dataset", help="Dataset name.")
	args = parser.parse_args()

	if args.dataset == "acme_1vm":
		Xy = pd.read_csv('../data/acme_interference_1vm.csv')
	elif args.dataset == "acme_2vm":
		Xy = pd.read_csv('../data/acme_interference_2vm.csv')
	elif args.dataset == "stress_1vm":
		Xy = pd.read_csv('../data/stress_ng_interference_1vm.csv')
	elif args.dataset == "stress_2vm":
		Xy = pd.read_csv('../data/stress_ng_interference_2vm.csv')
	elif args.dataset == "iot_1vm":
		Xy = pd.read_csv('../data/iot_interference_1vm.csv')
	elif args.dataset == "iot_2vm":
		Xy = pd.read_csv('../data/iot_interference_2vm.csv')

	Xy = select_data_subset(Xy)

	h2o.init()

	Xy = Xy.sample(frac=1).reset_index(drop=True)

	labels = Xy['total_time']
	data = Xy.drop(['total_time'], axis=1)

	X_train, X_test, y_train, y_test = train_test_split(data, labels, 
                                                    test_size=0.2)

	train = X_train
	train['total_time'] = y_train
	test = X_test
	test['total_time'] = y_test

	print('Training and Evaluating Static Models')

	automl_mape = automl_predict(train, test, max_runtime_secs=900)
	lr_mape = linear_regr_predict(train, test)

	print('AutoML MAPE: ' + str(automl_mape))
	print('Linear Regression MAPE: ' + str(lr_mape))
	