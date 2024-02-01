# %%

# Standard Library Imports

# Global Imports
import flowkit as fk
import pandas as pd
import numpy as np

# Local Imports
from .to_database import to_database

# ----------------------------------------
# Supporting Functions
# ----------------------------------------

def _clean_quadrant_name(gate_name: str) -> str:
    # Quadrant gate names suck.  This makes them better
    out_name_list = gate_name.split(': ')[-1].split(' , ')
    out_name_list = [x.split('-')[0] + x.strip(' ')[-1] for x in out_name_list]
    out_name = ', '.join(out_name_list)
    return out_name


def _is_quadrant_gate(gate) -> bool:
    if gate.gate_type == 'RectangleGate' and len(gate.dimensions) == 2:
        gate_name = gate.gate_name
        return len(gate_name) > 12 and gate_name[0] == 'Q' and all([x in gate_name for x in [':', '-', ',']])
    else:
        return False


def _clean_name(gate) -> str:
    cleaned_name = gate.gate_name
    if _is_quadrant_gate(gate):
        cleaned_name = _clean_quadrant_name(cleaned_name)
    return cleaned_name


def _is_rectangle(gate) -> bool:
    gate_type = gate.gate_type
    num_of_dims = len(gate.dimensions)
    if gate_type == 'RectangleGate':
        if num_of_dims == 1 or _is_quadrant_gate(gate):
            return True
    return False


def _find_linear_gate_boundry(
        gate,
        original_name,
        dimension_index=0,
        gate_name=None
):
    if not gate_name:
        gate_name = gate.gate_name

    boundry_dict = {
        'channel': gate.dimensions[dimension_index].id,
        'name': gate_name.replace('+', '').replace('-', ''),
        'deconstructed_from': original_name
    }

    if gate_name[-1] == '+':
        boundry_dict['value'] = gate.dimensions[dimension_index].min
    elif gate_name[-1] == '-':
        boundry_dict['value'] = gate.dimensions[dimension_index].max
    return boundry_dict


def _rectangle_unpacker(gate) -> list:
    boundaries = []
    gate_name = gate.gate_name
    if _is_quadrant_gate(gate):
        clean_gate_name = _clean_quadrant_name(gate_name)
        for i, sub_gate in enumerate(clean_gate_name.split(', ')):
            boundaries.append(_find_linear_gate_boundry(
                gate=gate,
                original_name=gate_name,
                dimension_index=i,
                gate_name=sub_gate))

    else:
        boundaries.append(
            _find_linear_gate_boundry(
                gate=gate,
                original_name=gate_name
            )
        )
    return boundaries


def _get_relevant_channels(
        gating_strategy_dict: dict,
        running_ids: dict
) -> dict:
    # Channels which are used in the gating strategy are the relevant ones
    channel_list = []
    running_ids['channel'] += 7
    for gate_dict in gating_strategy_dict:
        gate = gate_dict['gate']
        dimension_ids = [x.id for x in gate.dimensions]
        channel_list = channel_list + dimension_ids
    # Some channels are redundant
    channel_list = list(set(channel_list))
    channel_list = sorted(channel_list, key=lambda x: (x[0], x[2], x[-1]))
    channel_dict = {}
    for channel in channel_list:
        channel_dict[channel] = {
            'id': running_ids['channel'],
            'channel_label': channel,
            'experiment_id': running_ids['experiment']
        }
        running_ids['channel'] += 1
    return channel_dict


def _upload_gates(
        gating_strategy_list: list,
):
    gate_list = []
    for gate_dict in gating_strategy_list:
        gate_list.append(
                {
                    'id': gate_dict['gate_id'],
                    'experiment_id': gate_dict['experiment_id'],
                    'sample_group_id': gate_dict['group_id'],
                    'gate_name': gate_dict['clean_name'],
                    'gate_label': gate_dict['original_name'],
                    'parent_id': gate_dict['parent_id'],
                    'is_linear': gate_dict['is_linear']
                }
        )
    gate_df = pd.DataFrame(gate_list)
    gate_df.to_csv("test.csv")
    to_database(
        gate_df,
        'gates'
    )
    return gate_list, gate_df


def _upload_channels(
    relevant_channels: list
):
    channel_df = pd.DataFrame(relevant_channels)
    to_database(channel_df, 'channels')


def _upload_scalers(
        linear_boundaries: list,
):
    scaler_df = []
    complete_boundaries = [x for x in linear_boundaries if 'value' in x]
    for scaler in complete_boundaries:
        scaler_df.append({
                    'id': scaler['id'],
                    'channel_id': scaler['channel_id'],
                    'parent_id': scaler['parent_id'],
                    'boundry': scaler['value']
                })
    scaler_df = pd.DataFrame(scaler_df)
    to_database(
        scaler_df,
        'linear_scalers'
    )


# ----------------------------------------
# Main Functions
# ----------------------------------------


def get_gating_info(
    workspace: fk.Workspace,
    running_ids: dict,
    sample_group: str
) -> tuple:
    """
    Pulls information about each gate/channel in a flowkit session.

    Args:
        workspace: flowkit Workspace object
        starting_id: The next available gate id
        sample_group: The relevant sample group to analyze
    Returns:
        Gate information list, 
        Channel information list
    """

    gating_strategy_dict = {}
    
    # Assuming the first sample of the group is representative
    rep_sample = workspace.get_sample_ids(sample_group)[0] # Assuming the first sample of the group is representative
    
    gate_tuples = workspace.get_gate_ids(rep_sample)
    running_ids['gate'] += 4
    experiment_id = running_ids['experiment']
    group_id = running_ids['sample_group']

    # Scalers are different from gates, but very similar in function so they are extracted along gates
    linear_boundaries = []

    # Sorting by length of gate path should ensure that parent gates are unpacked before their children
    gate_tuples = sorted(
        gate_tuples,
        key=lambda x: len(x[1]))

    # Unpacking and expanding the generic .get_gate_ids() output
    for name, path in gate_tuples:
        gate = workspace.get_gate(
            sample_id=rep_sample,
            gate_name=name,
            gate_path=path
        )
        running_ids['gate'] += 1
        gate_info = {
            'gate_id': running_ids['gate'],
            'original_name': name,
            'path': path,
            'gate': gate,
            'experiment_id': experiment_id,
            'is_linear': gate.dimensions == 1,
            'sample_group': sample_group,
            'group_id': group_id,
            'clean_name': _clean_name(gate)
        }
        # Previous sorting of tuples ensures that parents are unpacked before children
        if len(path) > 1:
            gate_info['parent_id'] = gating_strategy_dict[path[-1]]['gate_id']
        else:
            gate_info['parent_id'] = None

        # Grab scalers while we can:
        if _is_rectangle(gate):
            linear_boundaries = linear_boundaries + _rectangle_unpacker(gate)

        # For some reason there are some gating strategies which have multiple gates of the same name
        if name in gating_strategy_dict:
            name = name + " again"
            gate_info['clean_name'] = gate_info['clean_name'] + " again"
            

        gating_strategy_dict[name] = gate_info
    
    # A dictionary was helpful when assigning parent IDs and such, 
    #   but now it needs to be a list
    gating_strategy_list = list(gating_strategy_dict.values())

    # Get channels
    channel_dict = _get_relevant_channels(
        gating_strategy_list,
        running_ids
    )

    scaler_id = running_ids['linear_scaler']

    # Add scaler parents from gating_info
    scaler_id += 2
    for scaler in linear_boundaries:
        source_name = scaler['deconstructed_from']
        source_info = gating_strategy_dict[source_name]
        scaler['parent_id'] = source_info['parent_id']
        scaler['channel_id'] = channel_dict[scaler['channel']]['id']
        scaler['id'] = scaler_id
        scaler_id += 1

    # A dictionary was helpful when assigning IDs and such, 
    #   but now it needs to be a list
    channel_list = list(channel_dict.values())

    _upload_gates(gating_strategy_list)
    _upload_channels(channel_list)
    _upload_scalers(linear_boundaries)

    running_ids['linear_scaler'] = scaler_id

    return gating_strategy_list, channel_list


# At time of making, redundant with session.get_gate_membership()
# I made it here to give it a more readable and meaningful docstring and such.
def sample_gate_membership(
    fk_sample_id: str,
    workspace: fk.Workspace,
    gate_info: dict
) -> np.array:
    """
    Grabs a membership vector for a a given sample of a given gate

    Args:
        sample_id: the sample ID as assigned by flowkit (not our internal ID)
        session: flowkit Session object
        gate_info: gate_info dict as output by get_gating_info()

    Returns:
        Numpy array of membership vector
        Array still needs event_id column. 
        Events in array are in the same order as returned by the fk.Session.get_gate_events()
    """
    flowkit_name = gate_info['original_name']
    path = gate_info['path']
    membership_array = workspace.get_gate_membership(
        sample_id = fk_sample_id,
        gate_name = flowkit_name,
        gate_path = path
    )
    return membership_array

# %%
