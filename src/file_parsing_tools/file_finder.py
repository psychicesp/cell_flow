# %%
# Standard Library Imports
import os

# Local Imports
from .wsp_parser import samples_from_wsp

# ----------------------------------------
# Supporting Functions
# ----------------------------------------


file_system_separator = os.path.sep[0] # I need an os agnostic way to split on file separator


def _find_flow_files(
        project_folder: str,
        sample_extension: str,
        workspace_extension: str) -> tuple:
    # Loops through all subdirectories in project folder sorting relevant files into
    # either the samples or workspace list based on supplied extension.
    workspaces = set()
    samples = set()
    flow_extensions = [sample_extension, workspace_extension]
    for subfolder, directory_name, files in os.walk(project_folder):
        relative_directory = os.path.relpath(subfolder, project_folder)
        for file in files:
            file_extension = file.split('.')[-1]
            if file_extension in flow_extensions:
                file_path = os.path.join(
                    project_folder,
                    relative_directory,
                    file)
                if file_extension == workspace_extension:
                    workspaces.add(file_path)
                else:
                    samples.add(file_path)
    return list(samples), list(workspaces)


def _group_into_experiments(
        samples: list, 
        workspaces: list) -> list:
    # Associates samples to workspaces based on information in the workspace xml.
    # Packages them into a dictionary.

    file_groups = []
    for workspace in workspaces:
        wsp_samples = samples_from_wsp(workspace)
        experiment_samples = [x for x in samples if x.split(
            file_system_separator)[-1] in wsp_samples]
        experiment_dict = {
            'workspace': workspace,
            'samples': experiment_samples
        }
        file_groups.append(experiment_dict)
    return file_groups

# ----------------------------------------
# Main Function
# ----------------------------------------

def get_grouped_files(
        project_folder: str,
        sample_extension ='fcs',
        workspace_extension ='wsp') -> list:
    """
    Loops through all subfolders of a project directory and finds related files;
    Organized into dictionaries with samples associated with workspaces.

    Args:
        project_folder: A file path to project file containing directory as a string
        sample_extension: The extension designated to sample files
        workspace_extension: The extesnion designated to workspace files

    Returns:
        A list of dictionaries structured as follows:
        [
            {
            workspace: File location of a workspace file,
            samples: [List of file locations to the samples associated with the experiment]
            }
        ]
    """
    samples, experiments = _find_flow_files(
        project_folder, sample_extension, workspace_extension)
    file_groups = _group_into_experiments(samples, experiments)
    return file_groups
# %%
