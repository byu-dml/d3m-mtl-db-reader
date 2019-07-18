import matplotlib.pyplot as plt

from src.analyses.analysis import Analysis
from src.utils import has_path
from src.entities.pipeline import Pipeline
from src.entities.primitive import Primitive
from src.utils import set_default


class BasicStatsAnalysis(Analysis):
    """
    An analysis that considers basic statistics and features of the
    pipeline run data. 
    """

    def run(self, dataset: dict, verbose: bool):

        # config
        num_top_primitives = 10

        # How many runs are there?
        num_runs = len(dataset.keys())
        # What is the distribution of pipeline run scores by metric type?
        metric_values: dict = {}
        # What is the distribution of phase types?
        phase_cnts: dict = {}
        # What is the distribution of metric types?
        metric_types_cnt: dict = {}
        # What is the distribution of number of datasets per run?
        dataset_cnt: dict = {}
        # How many pipeline runs include a normalized value with their metrics?
        num_normalized_metric_values = 0
        # Which primitives are most common?
        primitives_cnt: dict = {}
        # How many sub-pipelines are being used?
        num_subpipelines = 0

        for run in dataset.values():

            for step in run.pipeline.steps:
                if isinstance(step, Primitive):
                    set_default(primitives_cnt, step.python_path, 0)
                    primitives_cnt[step.python_path] += 1
                elif isinstance(step, Pipeline):
                    num_subpipelines += 1

            for score in run.scores:
                set_default(metric_values, score.metric, [])
                metric_values[score.metric].append(score.value)

            num_datasets = len(run.dataset_digests)
            set_default(dataset_cnt, num_datasets, 0)
            dataset_cnt[num_datasets] += 1

            for score in run.scores:
                set_default(metric_types_cnt, score.metric, 0)
                metric_types_cnt[score.metric] += 1
                if verbose:
                    print(
                        f"metric={score.metric}\tvalue={score.value}\tnormalized_value={score.normalized_value}"
                    )

                if score.normalized_value is not None:
                    num_normalized_metric_values += 1

            set_default(phase_cnts, run.run_phase, 0)
            phase_cnts[run.run_phase] += 1

        # Sort the primitive counts to get the most common
        primitives_cnt_tuples = primitives_cnt.items()
        primitives_cnt_tuples = sorted(
            primitives_cnt_tuples, key=lambda toop: toop[1], reverse=True
        )

        # Report

        print("\n*********************")
        print("****** RESULTS ******")
        print("*********************\n")

        for metric_type, metric_values in metric_values.items():
            plt.hist(metric_values, bins=20)
            plt.xlabel("score")
            plt.ylabel("count")
            plt.title(
                f"Distribution of {metric_type} Scores Across Pipeline Runs ({len(metric_values)} runs)"
            )
            plt.show()

        print(f"The dataset has {num_runs} pipeline runs with unique ids.")
        print(f"The distribution of run phases is: {phase_cnts}")
        print(f"The distribution of metric types is: {metric_types_cnt}")

        print(f"The distribution of datasets per run is: {dataset_cnt}")
        print(
            f"There are {num_normalized_metric_values} normalized metric values found among the pipelines"
        )
        print(f"The {num_top_primitives} most commonly used primitives are:")
        for prim_cnt in primitives_cnt_tuples[:num_top_primitives]:
            print(f"\t{prim_cnt[0]}\t{prim_cnt[1]}")
        print(f"There are {num_subpipelines} sub-pipelines found among the runs")