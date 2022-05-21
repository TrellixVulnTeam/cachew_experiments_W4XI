import pandas as pd
import numpy as np
import json
import yaml
import matplotlib
from matplotlib import pyplot as plt

# python3 plot.py --data caching_decision_inflate_2.5_b900_redo_agg_results.csv


from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string("data", None, "The csv file for the source data to plot.")
flags.DEFINE_string("caching_decision", None, "The csv file for the caching decision as generated by extract_decision.sh.")
flags.DEFINE_string("config", None, "The yaml config file (if any)")

def get_caching_decision(filename):
    df: pd.DataFrame
    df = pd.read_csv(filename) #type: ignore

    # remove all PROFILE rows
    df = df[df.decision != "PROFILE"]

    # map strings to cachew decisions
    df.decision = df.decision.map({
                        "GET_SOURCE": "source",
                        "PUT_SOURCE": "source",
                        "GET": "cache",
                        "PUT": "cache",
                        "COMPUTE": "compute",
                    }) 

    # check for unknown decision values
    if df.decision.isna().values.any():
        print("WARNING: there are unexpected values in the caching decision file ({}). Trying to continue, but maybe regenerate that file. ".format(filename))
        df= df.dropna() #type: ignore
    
    df = df.groupby("sleep_time_msec").agg({"decision": lambda x: pd.Series.mode(x)[0]}).sort_index()
    return pd.get_dummies(df.decision)

def main(argv):
    del argv
    if FLAGS.data is None:
        print("Please supply a filename for the source data.")
        exit(1)

    if FLAGS.caching_decision is None:
        print("Please supply a filename for the caching decision data.")
        exit(1)



    #with open(FLAGS.config) as config_file:
    #    exp_config = yaml.safe_load(config_file.read())

    num_rows = 556 # 556 for batch size 900 and 834 for batch size 900

    df = pd.read_csv(FLAGS.data) #.set_index("experiment/pipeline/params/sleep_time_msec") #type: ignore


    # Variables for plotting:
    x_start = 198
    y_start = 198
    x_end = 500
    y_end = 500

    x_label = "Per-batch data processing time injection (msec)"
    y_label = "Total time per batch (msec)"

    df_cachew_raw = df.loc[df['experiment/deployment/params/cache_policy'] == 5]
    df_compute = df.loc[df['experiment/deployment/params/cache_policy'] == 2]
    df_cache = df.loc[df['experiment/deployment/params/cache_policy'] == 3]
    df_source_cache = df.loc[df['experiment/deployment/params/cache_policy'] == 4]
    df_cachew_source = df_source_cache[0:4]
    df_cachew_compute = df_compute[4:5]
    df_cachew_cache = df_cache[5:7]

    df_decision = get_caching_decision(FLAGS.caching_decision)


    sleep_times = df_compute["experiment/pipeline/params/sleep_time_msec"].values[:]

    compute_times = 1000 * df_compute["avg"].values[:] / (num_rows)
    cachew_raw_times = 1000 * df_cachew_raw["avg"].values[:] / (num_rows)

    cache_times = 1000 * df_cache["avg"].values[:] / (num_rows)
    source_cache_times = 1000 * df_source_cache["avg"].values[:] / (num_rows)

    compute_std = 1000 * df_compute["std"].values[:] / (num_rows)
    cache_std = 1000 * df_cache["std"].values[:] / (num_rows)
    source_cache_std = 1000 * df_source_cache["std"].values[:] / (num_rows)
    
    zero = np.repeat(0, len(cache_times))
    cachew_times = np.repeat(0, len(cache_times))
    
    for dec,times in zip(["cache", "compute", "source"], [cache_times, compute_times, source_cache_times]):
        if dec in df_decision:
            if not len(cachew_times) == len(df_decision[dec]) and len(cachew_times) == len(times):
                print("WARNING: the dimensions for the vectors describing the caching decisions do not match. Please report contents of the cachew_decision.csv.")
                continue
            cachew_times += df_decision[dec].mul(times)

    plt.rcParams.update({'font.size': 18})
    plt.rcParams.update({'figure.figsize':(10, 4)}) 

    #plt.figure(1, figsize=(4.5, 2.25))
    #plt.figure(1)
    #plt.title(title)
#    plt.axis([x_start, x_end, y_start, y_end])
    plt.grid(color='lightgrey', linestyle=':', linewidth=1)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    #plt.yticks(range(0, 10, 1))
    #plt.xticks(range(0, 550000000, 100000000))
    #plt.xscale('symlog')
    #plt.yscale('symlog')
    #plt.tight_layout()
    plt.errorbar(sleep_times[:len(compute_times)], compute_times, compute_std, fmt='+-', label="Compute", color=(0.36, 0.54, 0.66), linewidth=2, elinewidth=1, capsize=1.3)
    plt.errorbar(sleep_times[:len(source_cache_times)], source_cache_times, source_cache_std, fmt='x-', label="Source cache", color=(0.57, 0.36, 0.51), linewidth=2, elinewidth=1, capsize=1.3)
    plt.errorbar(sleep_times[:len(cache_times)], cache_times, cache_std, fmt='^-', label="Full Cache", color=(0.53, 0.66, 0.42), linewidth=2, elinewidth=1, capsize=1.3)
    plt.plot(sleep_times[:len(cachew_times)], cachew_times, marker='o', label="Cachew", color='orange', linewidth=10, alpha=0.6)
#    plt.plot(sleep_times[:len(cachew_raw_times)], cachew_raw_times, marker='o', label="Cachew Raw", color='pink', linewidth=10, alpha=0.6)
    plt.legend(frameon=False, loc='lower right')

    dest_name = FLAGS.data
    dest_name = "./time_per_row_highlight.png"
    print("plot saved at " + dest_name)
    plt.tight_layout()
    plt.savefig(dest_name)

    # Variables for plotting:
    x_start = y_start = 0
    x_end = 800
    y_end = 1300

    """
    title = "Average throughput with varying row sizes"
    x_label = "bytes per row [MB]"
    y_label = "Throughput [MB/sec]"

    tps = (labels / avgs)
    df["tp"] = tps

    plt.figure(2, figsize=(4.5, 2.25))
    plt.title(title)
    #plt.axis([x_start, x_end, y_start, y_end])
    plt.grid(color='lightgrey', linestyle='-', linewidth=1)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    #plt.yticks(range(0, 10, 1))
    #plt.xticks(range(0, 550000000, 100000000))
    #plt.xscale('symlog')
    #plt.yscale('symlog')
    plt.legend(frameon=False, loc='best')
    plt.tight_layout()
    plt.plot(labels, tps, label="Filestore", color=(0.36, 0.54, 0.66))

    dest_name = FLAGS.data
    dest_name = dest_name.split(".")[0] + "_tp.png"
    plt.savefig(dest_name)"""


    # TODO use plt...
    #ax = df.plot(x="labels", y="avg", yerr="std", kind="line", figsize=(4.5, 2.25), use_index=False, legend="True", loglog=False)
    #plt.plot(labels, avgs, yerr=stds, kind="line", figsize=(4.5, 2.25), legend="True", loglog=False)
    #plt.switch_backend('TkAgg')


    #plt.show()

    #df.to_csv("agg.csv", index=False)

    #     stats = json.load(json_file)
    #
    # stats = stats["sysstat"]["hosts"][0]["statistics"][0]
    # print(stats)



if __name__ == '__main__':
    app.run(main)
