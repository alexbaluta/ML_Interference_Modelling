import argparse
import h2o
import numpy as np
import pandas as pd
import time

from h2o.automl import H2OAutoML
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Sum, RBF, RationalQuadratic
from statistics import mean

def window_predict(df, model_type, window_step_size=7):
	"""
	Applies a window function over a dataframe. Models of type model_type are trained on
	each window and the average MAE is computed over all windows.

	Parameters: 
    df (Pandas DataFrame): Input dataframe
    model_type: The model type to train and evaluate
	"""
	
	mape_lst = []

	lower = 0
	upper = 199

	while upper + window_step_size < len(df):
		train = df[lower:upper]
		test = df[upper+1:upper+window_step_size]

		if model_type == 'Gaussian':
			mape_lst.append(gp_regr_predict(train, test))
		elif model_type == 'AutoML':
			try:
				automl_mape = automl_predict(train, test, 30)
				mape_lst.append(automl_mape)
			except:
				try:
					h2o.shutdown(prompt=False)
				finally:	
					print("Failed to connect to running h2o server. Initializing new one in 2 min.")
					time.sleep(120)
					h2o.init()
					automl_mape = automl_predict(train, test, 30)
				mape_lst.append(automl_mape)
		else: 
			raise Exception("Invalid Model input into Sliding Window Function")

		lower = lower + window_step_size
		upper = upper + window_step_size

		print("Progress: " + str(upper / df.shape[0] * 100) + "%")

	avg_mape = mean(mape_lst)

	return avg_mape

def shuffle_within_group(df, columns):
	groups = [df for _, df in df.groupby(columns)]
	groups = [df.sample(frac=1).reset_index(drop=True) for df in groups]
	return pd.concat(groups)

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

def gp_regr_predict(train, test):
	"""
	Use gaussian process to learn a regressor on the input train set. 
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

	kernel = Sum(RBF(), RationalQuadratic())
	regr = GaussianProcessRegressor(kernel=kernel, copy_X_train=False).fit(train_X, train_y)
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
	parser.add_argument("-W", "--workload", help="Workload structure.")
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

	if args.workload == "all_ordered":
		pass
	elif args.workload == "target_app_ordered":
		Xy = shuffle_within_group(Xy, ["httperf_num", "httperf_per"])
	elif args.workload == "random":
		Xy = Xy.sample(frac=1).reset_index(drop=True)
		
	Xy = Xy.drop(columns=['httperf_num', 'httperf_per'])

	h2o.init()

	print('Training and Evaluating Dynamic Models')

	automl_mape = window_predict(Xy, "AutoML", 300)
	gaussian_mape = window_predict(Xy, "Gaussian", 300)

	print("AutoML: " + str(automl_mape))
	print("Gaussian: " + str(gaussian_mape))
