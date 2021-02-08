# How to run an experiment

1. Run the experiment as follows, e.g. `python3 -m experiments.system_model_v3.experiment_`
2. Check `experiment_run_log.md` for experiment details, such as data store key
3. Check the logs in experiment `logs/` directory and the results in experiment `experiment_results.hdf5` store, with key for each new experiment
4. Process results using `post_process.py` from notebook
5. Analyze post-processed results
6. Make notes in `experiment_run_log.md` about experiment results
