![cachew-logo](docs/figures/cachew_logo.png)

# Cachew: ML Input Data Processing as a Service

Cachew is a multi-tenant service for efficient input data processing in machine learning jobs. To minimize end-to-end training time and cost, Cachew jointly optimizes: 1) elastic, distributed resource allocation for input data processing and 2) input data caching and materialization of preprocessed data within and across jobs. Cachew builds on top of the [tf.data](http://vldb.org/pvldb/vol14/p2945-klimovic.pdf) data loading framework in [TensorFlow](https://github.com/tensorflow/tensorflow), extending [tf.data service](https://www.tensorflow.org/api_docs/python/tf/data/experimental/service) with autoscaling and autocaching policies.  

This repository contains instructions for deploying Cachew in Google Cloud and using the service to efficiently execute ML input data pipelines. To view the source code for Cachew, please go to: [https://github.com/eth-easl/cachew](https://github.com/eth-easl/cachew). 


## Cachew System Architecture

Cachew consists of a centralized dispatcher, a dynamic number of input data workers, and a disaggregated storage cluster for data caching.

![cachew-system-architecture](docs/figures/cachew_system_arch.png?raw=true)

Users register training nodes (i.e., clients) of ML training jobs with the Cachew dispatcher. Clients provide a dataflow graph representation of their input pipeline and a path to the input dataset. Users can annotate the input pipeline to mark candidate locations for caching/reusing data across executions (e.g., before any data transformations in the input pipeline that introduce randomness to improve model accuracy). Cachew will automatically apply caching at the throughput-optimal location in the input pipeline among the candidate locations. Cachew supports and extends the tf.data API for defining input data pipelines from a collection of composable and user-parametrizable operators. 

Cachew's input data workers are stateless components responsible for producing batches of preprocessed data for clients. The dispatcher dynamically adjusts the number of input data workers for each job to minimize epoch time while keeping costs low. The dispatcher also profiles and maintains metadata about input pipeline executions across jobs to make data caching decisions. Cachew stores cached datasets in a GlusterFS remote storage cluster. 

Clients fetch data from the workers that are assigned to them by the dispatcher. Clients and workers periodically send heartbeats to the dispatcher to maintain membership in the service and provide metrics used for the autoscaling and autocaching policies.


## Getting Started

### Deploying a Cachew cluster
TODO: instruction/script to deploy a single worker cluster.

### Writing an ML input data pipeline for Cachew
TODO: basic tf.data pipeline example.

### Executing an ML input data pipeline with Cachew
TODO: instructions/script to run experiment. 

## Detailed Instructions 

TODO: link to instructions for reproducing figures in paper. 

## Contributing

We welcome contributions to Cachew. Please see our [Cachew source code](https://github.com/eth-easl/cachew) repository.

 
## Referencing our work

Cachew will appear at USENIX ATC'22. If you decide to use Cachew in your work, please cite our paper: 

```
@inproceedings{cachew,
  author    = {Dan Graur and
               Damien Aymon and
               Dan Kluser and
               Tanguy Albrici and
               Chandramohan A. Thekkath and
               Ana Klimovic},
  title     = {Cachew: Machine Learning Input Data Processing as a Service},
  booktitle = {Proceedings of the USENIX Annual Technical Confernece (ATC'22)},
  publisher = {{USENIX}},
  year      = {2022},
}
```

