#%%
# Standard Imports
import re
import os

# ----------------------------------------
# Supporting Functions
# ----------------------------------------

# I'm sure there is a better way to get an absolute path to the module  
#   which works wherever this module is run from,
#   but I'm tired and I need to get this to work quickly
module_path = __file__.split('cell_flow')[0] + 'cell_flow'
queries_path = os.path.join(module_path, 'src', 'sql', 'queries')

def _open_query(file_name: str)->str:
    # Reads a query text given file name

    file_name = os.path.basename(file_name)
    if '.sql' not in file_name:
        file_name = file_name + '.sql'
    file_location = os.path.join(queries_path, file_name)
    with open(file_location, 'r') as sql_file:
        query_text = sql_file.read()

    return query_text


# ----------------------------------------
# Main Function
# ----------------------------------------


def get_sql_query(
        file_name: str,
        require_kwargs=True,
        allow_extra_kwargs=False,
        verbose=True,
        **kwargs
) -> str:
    """
    Replaces placeholders in a sql query with values supplied as kwargs

    Args:
        file_name:          Name of file in 'queries' folder 
        require_kwargs:     Throw errors if placeholders in query are not matched with supplied kwargs
        allow_extra_kwargs: Will proceed even if kwargs are supplied which do not match placeholders
        verbose:            Will print missing/extra information.  Useful if error-catching is disabled.
        **kwargs:           Values to replace matching placeholders, ie (table = 'big_table' will replace ':table' with 'big_table')

    Returns:
        A SQL query as a string
    """

    query = _open_query(file_name)

    # Error handling for missing kwargs
    placeholders = set(re.findall(r"{\w+}", query))
    placeholders = [x.strip('{').strip('}') for x in placeholders]
    missing = placeholders.copy() 
    for kwarg in list(kwargs.keys()):
        missing.remove(kwarg)
    if missing:
        if require_kwargs:
            raise ValueError(f"Missing keyword arguments: {missing}")
        elif verbose:
            print(f"Missing keyword arguments: {missing}")

    # Error handling for extra kwargs
        extra = list(kwargs.keys())
        for placeholder in placeholders:
            if placeholder in extra:
                extra.remove(placeholder)
        if extra and not allow_extra_kwargs:
            raise ValueError(f"Unused keyword arguments: {extra}")
        elif verbose:
            print(f"Unused keyword arguments: {extra}")
    
    if not require_kwargs:
        for miss in missing:

            # this was a pain with f-strings so here we are
            bracketed_miss = '{' + miss + '}'

            query = query.replace(bracketed_miss, miss)

    # kwargs need to be wrapped in quotes to minimize sql errors
    quotified_kwargs = {key: f'"{value}"' for key, value in kwargs.items()}


    return query.format(**kwargs)


# %%
