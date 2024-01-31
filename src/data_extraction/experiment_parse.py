# Standard Library Imports
import os
import time

# Global Imports
import flowkit as fk
import pandas as pd

# Local Imports
from .metadata_parse import metadata_from_sample_list
from .gate_parse import get_gating_info
from .group_parse import get_group_info
from .to_database import to_database
from .sample_parse import read_sample

# ----------------------------------------
# Supporting Functions
# ----------------------------------------
start_time = time.time()
current_sample_count = 0


def _log_print(statement):
    global current_sample_count
    current_time = time.time()
    elapsed_time = (current_time-start_time)/60
    if current_sample_count > 0:
        per_sample = elapsed_time/current_sample_count
        extra_statement = f"Sample #: {current_sample_count}; {round(elapsed_time, 2)}m Elapsed; {round(per_sample, 2)} per"
    else:
        extra_statement = f"Sample #: {current_sample_count}; {round(elapsed_time, 2)}m Elapsed"

    current_sample_count = current_sample_count + 1 
    print("         ", statement, extra_statement)


def _cytokine_doe_sorter(file_name):
    if 'compensation' in file_name.lower():
        file_name = 'zzzz' + file_name
    return file_name


def _is_control(sample_name: str):
    lower_sample_name = sample_name.lower()
    return (
        'no cyt' in lower_sample_name or
        'sample.fcs' in lower_sample_name or
        '_baseline_' in lower_sample_name or
        lower_sample_name.split(' ')[0][:2] == 'wt'
    )


# ----------------------------------------
# Main Function
# ----------------------------------------


def read_experiment(
        grouped_experiment,
        running_ids
        ):
    sample_files = grouped_experiment['samples']
    workspace_file = grouped_experiment['workspace']
    experiment_name = os.path.basename(workspace_file)
    print(f"    {experiment_name}")

    experiment_df = pd.DataFrame(
        [
            {
                'id': running_ids['experiment'],
                'experiment_name': experiment_name,
                'project_id': running_ids['project']
            }
        ]
    )

    to_database(experiment_df, 'experiments')

    workspace = fk.Workspace(workspace_file, sample_files, ignore_missing_files=True)

    sample_group = get_group_info(workspace, running_ids)

    gating_strategy, channel_info = get_gating_info(
        workspace=workspace,
        running_ids=running_ids,
        sample_group=sample_group
    )
    sample_names = sorted(workspace.get_sample_ids(sample_group), key = _cytokine_doe_sorter)
    next_event_id = running_ids['event']

    all_metadata = metadata_from_sample_list(sample_names)

    workspace.analyze_samples(
        group_name=sample_group
        )

    for sample_name in sample_names:
        sample_metadata = all_metadata.get(sample_name, {})
        sample_object = workspace.get_sample(sample_name)
        event_count = sample_object.event_count + 1

        _log_print(sample_name)

        #   Passing the running_ids dict into the read_sample function would be a terrible idea
        # as the ultimate goal is to run that function as multiple jobs in asynchronous parallel.
        # hence pulling the value into a variable
        sample_id = running_ids['sample']

        sample_df = pd.DataFrame(
            [
                {
                    'id': sample_id,
                    'sample_name': sample_name,
                    'day': sample_metadata.get('day', ''),
                    'donor': sample_metadata.get('donor', ''),
                    'experiment_id': running_ids['experiment'],
                    'control': _is_control(sample_name)
                }
            ]
        )

        to_database(sample_df, 'samples')
        read_sample(
            workspace = workspace,
            sample_id = sample_name,
            experiment_id = running_ids['experiment'],
            next_event_id = next_event_id,
            rds_sample_id = sample_id,
            relevant_channels = channel_info,
            gating_strategy = gating_strategy
        )
        # Leaves the next integers reserved for the next job.
        next_event_id = next_event_id + event_count + 1
        running_ids['sample'] += 1

    # To leave a numeric gap between events of different experiments
    running_ids['event'] = next_event_id + 12

    running_ids['experiment'] += 1