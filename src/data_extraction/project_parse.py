# %%
# Standard Library Imports
import os

# Global Imports
import pandas as pd

# Local Imports
from ..sql.execute import create_all_views 
from ..file_parsing_tools.file_finder import get_grouped_files
from .next_ids import get_starting_ids
from .to_database import to_database
from .experiment_parse import read_experiment

# ----------------------------------------
# Main Function
# ----------------------------------------

def read_project(
    project_folder: str
    ) -> None:
    """
    Traverse a folder structure, associating .fcs files with .wsp, and extracting the data into SQL.
    This target folder must contain all .wsp and .fcs files associated with the project
    
    project_folder: path to the folder containing .wsp and .fsc files.
    """
    running_ids = get_starting_ids()
    project_name = os.path.basename(project_folder)
    project_files = get_grouped_files(project_folder)
    print(project_name)
    project_df = pd.DataFrame(
        [
            {
                'id': running_ids['project'],
                'project_name': project_name
            }
        ]
    )
    to_database(
        project_df,
        "projects"
    )

    for grouped_experiment in project_files:
        read_experiment(grouped_experiment, running_ids)
        running_ids['experiment'] += 1
    
    create_all_views(running_ids['project'])

