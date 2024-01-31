# Standard Library Imports

# Global Imports
import flowkit as fk
import numpy as np
import pandas as pd

# Local Imports
from .gate_parse import sample_gate_membership
from .column_parse import rename_to_channels
from .to_database import to_database

# ----------------------------------------
# Main
# ----------------------------------------


def read_sample(
    workspace: fk.Workspace,
    sample_id,
    experiment_id,
    next_event_id,
    rds_sample_id,
    relevant_channels,
    gating_strategy
):

    event_df = workspace.get_gate_events(
        sample_id
    )
    # TODO Filter df down to single correct column level

    event_id_array = np.arange(
        next_event_id, next_event_id + len(event_df))
    event_df['event_id'] = event_id_array
    event_df['sample_id'] = rds_sample_id
    event_df['random'] = np.random.rand(len(event_df)).astype('float32')

    # Populating the events table
    to_database(
        event_df.loc[:, ['event_id', 'sample_id', 'random']].rename(
            {'event_id': 'id'}, axis=1),
        'events'
    )
    relevant_channel_names = [x['channel_label'] for x in relevant_channels] + ['event_id']
    event_df = rename_to_channels(
        event_df,
        relevant_channel_names
    )
    event_df = event_df.loc[:, relevant_channel_names]

    fluor_table_name = f"{experiment_id}_fluorescence"
    membership_table_name = f"{experiment_id}_membership"

    to_database(event_df, fluor_table_name)

    membership_df = pd.DataFrame()

    for gate in gating_strategy:
        membership_array = sample_gate_membership(
            fk_sample_id=sample_id,
            workspace=workspace,
            gate_info=gate
        )
        membership_df[gate['clean_name']] = membership_array

    membership_df['event_id'] = event_id_array
    
    to_database(membership_df, membership_table_name)
