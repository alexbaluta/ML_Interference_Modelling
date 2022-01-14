# ML_Interference_Modelling

This repository contains artifacts that can be used to replicate experiments detailed in the paper titled "Machine Learning based Interference Modelling in Cloud-Native Applications". 

The data directory contains ordered performance interference data derived from several experiments. Our techniques can be run on this data to replicate at runtime predictions. The target application, or application of interest, in our experiments was Acme Air. In these experiments an interfering application was run alongside Acme Air. Furthermore, the target application and interfering application were deployed to a single VM or deployed across two VMs in these experiments. The file name denotes what interfering application and deployment strategy was used to generate the data within the file.

The scripts directory contains the static and dynamic modelling scripts which implement several performance interference modelling techniques including our Machine Learning based technique described in our paper. Before running this script, follow the instructions under the Getting Started section to install pre-requisite libraries. Afterwards, follow the Step-by-Step Instructions section to run the modelling scripts against the data file of your choice.

# Getting Started

The modelling scripts requires python 3, java, and several libraries to be installed on your machine. The techniques in our paper were run with the software listed below on a Ubuntu 16.04 host. Each of these should be installed on your machine prior to running the scripts. Follow the associated links below for detailed instructions to install each dependency. We recommend using [pip](https://pip.pypa.io/en/stable/), the package installer for python, to install libraries 3-6. 

1. [python](https://www.python.org/downloads/) version 3.7.1
2. [java](https://www.java.com/en/download/) version 8u311
3. [h2o](https://docs.h2o.ai/h2o/latest-stable/h2o-docs/downloading.html) version 3.34.0.3
4. [numpy](https://numpy.org/install/) version 1.16.1
5. [pandas](https://pandas.pydata.org/pandas-docs/version/0.25.1/install.html) version 0.25.1
6. [scikit-learn](https://scikit-learn.org/stable/install.html) version 0.24.2
7. [xgboost](https://xgboost.readthedocs.io/en/latest/install.html) version 1.3.3

# Step-by-Step Instructions

1. Ensure you have installed all pre-requisite software as described in the Getting Started section.
2. Clone this repository on to your machine.
3. Through command line, navigate to the scripts directory of this repository.
4. The static_modelling.py and dynamic_modelling.py scripts train models on data from a file in the data directory. Subsequently, the scripts evaluate the models and outputs MAPE metrics per model to standard out. Accordingly, both modelling scripts require a dataset argument set with "-D" or "--dataset". 
 
The following 6 datasets are supported:

* acme_1vm
* acme_2vm
* stress_1vm
* stress_2vm
* iot_1vm
* iot_2vm

The static_modelling.py script should be run from command line in the following format: python classification.py --dataset <datasetName>

Note that the static_modelling.py script will randomize the order of the data and apply an 80-20 train test split. In contrast, the dynamic_modelling.py script takes in an additional parameter "-W" or "--workload". This parameter specifies how the performance data should be structured. There are three options:

* all_ordered
* target_app_ordered
* random

The "all_ordered" workload structure represents a scenario in which both the target application workload and the interfering application workload are ordered by workload intensity. 
The "target_app_ordered" workload structure represents a scenario in which the target application workload is ordered by workload intensity and the interfering application workload is random. That is, there is structure to the target application workload and the intensity of the interfering application workload is unknown. In this scenario, an application owner knows the characteristics of workload traffic to their application and does not have visibility of the interfering application. In our paper, we present results obtained from using the "target_app_ordered" workload structure for modelling.
The "random" workload structure randomizes all data. There is no order.

The dynamic_modelling.py script should be run from command line in the following format: python classification.py --dataset <datasetName> --workload <workloadStructure>

 5. Once either of the scripts have run, the metrics are output to standard out in your terminal. Note that the dynamic_modelling.py script takes approximately 12 hours to run.

# Extending the Scripts

The scripts could be extended in several fashions. 
1. The static and dynamic modelling script can be further extended to evaluate additional algorithms. Users can implement those algorithms and evaluate their performance against our approach and competing techniques. In the case of the dynamic modelling script, additional algorithms can be integrated with the window_predict function, which is our model deployment strategy. 
2. Further work can be done to evaluate the effectiveness of different model deployment strategies. As mentioned, our work used a fixed time window model deployment strategy implemented by the window_predict function. Users can implement new strategies in which they invoke model training on a new criteria.
3. The static and dynamic modelling scripts could be further improved to encapsulate model training and model deployment strategies for use in container placement strategies. 