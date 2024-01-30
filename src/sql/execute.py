# %%
# Standard Imports

# Global Imports
import pandas as pd

# Local Imports
from .query_interpretation import get_sql_query
from .postgres import engine

# ----------------------------------------
# Supporting Functions
# ----------------------------------------


def _execute(
    query: str
):
    with engine.begin() as con:
        result = con.execute(query)
    return result


def _nuke():
    permission = input("Are you sure you'd like to clear the database? (y/N)")
    password = input("Password: ")
    # Password is not meant to be secure, but to reduce accidents
    if permission.lower() == 'y' and password == 'ABIn_Flow':
        nuke_query = get_sql_query('clear_everything.sql')
        result = _execute(nuke_query)
    return result


def _the_technology():
    # We can rebuild it
    query = get_sql_query(
        file_name="flow_schema.sql",
        require_kwargs=False,
        verbose=False
    )
    result = _execute(query)
    return result


def _get_all_table_ids(table):
    query = get_sql_query('all_table_ids.sql', table=table)
    with engine.begin() as con:
        table_ids = pd.read_sql(query, con)['id'].to_list()
    return table_ids


def _get_project_table_ids(
        table,
        project_id
):
    query = get_sql_query('project_table_ids.sql',
                          table=table, project_id=project_id)
    with engine.begin() as con:
        table_ids = pd.read_sql(query, con)['id'].to_list()
    return table_ids


def _full_experiment_query(
        experiment_id: int,
        table_type='fluorescence') -> str:
    experiment_name = f'"{experiment_id}_{table_type}"'
    query = f"""
        SELECT *
        FROM {experiment_name}
""".strip('\n')
    return query


def _create_project_view(
        project_number,
        table_type,
        experiment_ids=False
):
    if not experiment_ids:
        experiment_ids = _get_project_table_ids("experiments", project_number)
    header = f'CREATE OR REPLACE VIEW "project_{project_number}_{table_type}" AS \n'
    experiment_queries = [
        _full_experiment_query(x, table_type)
        for x in experiment_ids
        ]
    sub_query = '\nUNION ALL\n'.join(experiment_queries)
    query = f"""
    SELECT sub_query.*, events.random, samples.control
    FROM (
    {sub_query}
    ) AS sub_query
    LEFT JOIN events ON sub_query.event_id = events.id
    LEFT JOIN samples ON events.sample_id = samples.id
""".strip('\n')
    query = header + query
    result = _execute(query)
    return result


# def _create_project_membership(
#         project_number,
#         experiment_ids=False
# ):
#     if not experiment_ids:
#         experiment_ids = _get_project_table_ids("experiments", project_number)
#     query = f'CREATE OR REPLACE VIEW "project_{project_number}_membership" AS \n'
#     experiment_queries = [_full_experiment_query(x, 'membership') for x in experiment_ids]
#     experiment_queries = '\nUNION ALL\n'.join(experiment_queries)
#     query = query + experiment_queries + ';'
#     result = _execute(query)
#     return query



# ----------------------------------------
# Main Functions
# ----------------------------------------


def phoenix():
    """
    If you don't already know what this does, you have no business using it
    """
    result = _nuke()
    result = _the_technology()
    return result


def max_id(
        table: str
):
    query = get_sql_query(
        file_name="max_id.sql",
        table=table
    )
    result = _execute(query).fetchone()
    return result[0]


def create_all_views(project=False):
    if project:
        project_ids = [project]
    else:
        project_ids = _get_all_table_ids('projects')
    for project_id in project_ids:
        experiment_ids = _get_project_table_ids("experiments", project_id)
        _create_project_view(
            project_id,
            'fluorescence',
            experiment_ids
        )
        _create_project_view(
            project_id,
            'membership',
            experiment_ids
        )

# %%
