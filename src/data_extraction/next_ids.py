
# Local Imports
from ..sql.execute import max_id

tables_with_ids = [
    'projects',
    'experiments',
    'sample_groups',
    'samples',
    'events',
    'gates',
    'channels',
    'linear_scalers'
]

# ----------------------------------------
# Main Function
# ----------------------------------------

def get_starting_ids()->dict:
    """
    Returns: A dictionary of next_available_ids
    """

    id_dict = {}
    for table in tables_with_ids:
        if table[-1] == 's':
            depluralized_name = table[:-1]
        else:
            depluralized_name = table
        next_id = max_id(table)
        if not next_id:
            next_id = 1
        else:
            next_id += 1
        id_dict[depluralized_name] = next_id

    return id_dict