# %%
# Standard Library Imports


# Global Imports
import flowkit as fk
import pandas as pd

# Local Imports
from .to_database import to_database


# ----------------------------------------
# Supporting Functions
# ----------------------------------------

def _complexity_index(complexities, samples):
    if complexities and samples:
        return sum(complexities)/len(complexities) + len(samples)
    else:
        return 0

def _average_gate_complexity(
        workspace: fk.Workspace,
        sample_group: list
) -> str:
    complexities = 0
    samples = workspace.get_sample_ids(sample_group)
    for sample in samples:
        gate_complexity = len(workspace.get_gate_ids(sample))
        complexities += gate_complexity
    return complexities

def _get_relevant_group(
        workspace: fk.Workspace
) -> str:
    # TODO Get all groups with unique gating strategies/sample sets.
    sample_groups = workspace.get_sample_groups()
    gated_groups = sorted(sample_groups, key=lambda x: _average_gate_complexity(workspace, x))
    return gated_groups[-1]


def _upload_group(
        group_name: str,
        running_ids: dict
):
    group_df = pd.DataFrame(
        [
            {
                'id': running_ids['sample_group'],
                'sample_group': group_name,
                'experiment_id': running_ids['experiment']
            }
        ]
    )
    to_database(group_df, 'sample_groups')


# ----------------------------------------
# Main Function
# ----------------------------------------


def get_group_info(
        session: fk.Session,
        running_ids: dict
) -> str:
    """
    Grabs the name of the relevant group, assigns and id, 
    and injects its info into the database

    Args:
        session:  A session object with the appropriate workspace imported
        running_ids: A dictionary containing current iteration of ids.
    Returns:
        Name of the relevant group
    """
    relevant_group = _get_relevant_group(session)
    running_ids['sample_group'] += 1
    _upload_group(
        relevant_group,
        running_ids
    )
    return relevant_group