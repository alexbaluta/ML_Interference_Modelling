# General Data Structure

The following metrics below are common to both 1VM and 2VM experiments

* acme_db_cpu: The CPU utilization percentage of the target Acme Air application's Mongo DB database container.
* acme_db_mem: The Memory utilization percentage of the target Acme Air application's Mongo DB database container.
* acme_web_cpu: The CPU utilization percentage of the target Acme Air application's NodeJS Web server container.
* acme_web_mem: The Memory utilization percentage of the target Acme Air application's NodeJS Web server container.
* Time: The timestamp when the metrics were obtained.
* class: A boolean 0 or 1 value indicating whether performance interference is present or not. Note this metric is not used in our modelling scripts but can be used for other experimentation. This boolean was calculated by deriving a 95% confidence interval on the total request-response time without interference present. If the total request time exceeds the 95% interval thresholds, interference (1) is inferred. Else, no interference (0) is inferred.
* httperf_num: The httperf Workload Generator parameter that specifies the number of sessions to create to our target Acme Air application.
* httperf_per: The httperf Workload Generator parameter that specifies the time interval between sessions.
* request_rate: The realized throughput, or request rate, from our httperf Workload Generator to our target Acme Air application.
* interference_wkld_intensity: The workload intensity for the interfering application co-located alongside our target Acme Air application. Note that this metric is not standardized across interfering applications. But for any interfering application, the greater this metric is, the more workload intensity is sent to the respective interfering application.
* total_time: The total request-response time for a request sent to our target Acme Air application. This is a sum of the response time, transfer time, and connection time as reported by our httperf Workload Generator.

# Data Structure for 1VM Specific Metrics

The following metrics are found within the 1VM datasets. To note, in our 1VM experiments the target Acme Air appliction was hosted on a single VM. The metrics below are specific to that single VM.

* host_cpu: The Virtual Machine's CPU utilization percentage.
* host_mem: The Virtual Machine's Memory utilization percentage.

# Data Structure for 2VM Specific Metrics

The following metrics are found within the 2VM datasets. To note, in our 2VM experiments the target Acme Air appliction was distributed across two VMs. One VM hosted Acme Air's NodeJS Web server. The other VM hosted Acme Air's MongoDB Database.

* db_host_cpu: The CPU utilization percentage of the Virtual Machine hosting the target Acme Air's MongoDB database
* db_host_mem: The Memory utilization percentage of the Virtual Machine hosting the target Acme Air's MongoDB database
* web_host_cpu: The CPU utilization percentage of the Virtual Machine hosting the target Acme Air's NodeJS web server
* web_host_mem: The Memory utilization percentage of the Virtual Machine hosting the target Acme Air's NodeJS web server
