# Standard Library Imports
import regex as re

# Global Imports
import pandas as pd

# Local Imports

# ----------------------------------------
# Supporting Functions
# ----------------------------------------


def _index_by_given(
        df: pd.DataFrame,
        given_columns: list
) -> pd.DataFrame:
    desirable_matches = {}
    for multiindex_level in range(df.columns.nlevels):
        level_columns = df.columns.get_level_values(multiindex_level)
        columns_present = [x for x in given_columns if x in level_columns]
        match_index = len(columns_present)/len(given_columns)
        desirable_matches[multiindex_level] = match_index
    return desirable_matches


def _match_channels_to_columns(
        column_names: list,
        wanted_column_names: list
) -> dict:
    renamer = {}
    column_names = sorted(column_names, key = len, reverse=True)
    for column in column_names:
        matches = [x for x in wanted_column_names if column[:len(x)] == x]
        if len(matches) == 1:
            renamer[column] = matches[0]
    return renamer        

def _strip_excess_columns(
        df: pd.DataFrame,
        best_level: int
) -> pd.DataFrame:
    columns = df.columns.get_level_values(best_level)
    recolumned_df = pd.DataFrame(
        df.values,
        columns
    )
    return recolumned_df


# ----------------------------------------
# Main Functions
# ----------------------------------------

def rename_to_channels(
        df: pd.DataFrame,
        dimensions: list
) -> pd.DataFrame:
    column_names = list(df.columns)
    renamer = _match_channels_to_columns(
        column_names,
        dimensions
    )
    return df.rename(renamer, axis = 1)

def flatten_df_columns(
        df: pd.DataFrame,
        desirable_columns: list
) -> pd.DataFrame:
    """
    Blurb:

    Args:

    Returns:
    """

    match_levels = _index_by_given(df, desirable_columns)
    match_level = max(match_levels, key=lambda x: match_levels[x])
    flat_df = _strip_excess_columns(
        df,
        match_level)
    return flat_df



# ----------------------------------------
# Depreciated
# ----------------------------------------

# desirable_pattern = r'[A-Z]{2}[A-Z0-9]{1}-[AWH]'

# def _find_matching_level(
#         df: pd.DataFrame,
#         pattern
# ):
#     desirable_matches = {}
#     for multiindex_level in range(df.columns.nlevels):
#         column_names = df.columns.get_level_values(multiindex_level)
#         match_count = sum([1 for column in column_names if re.match(pattern, str(column))])
#         desirable_matches[multiindex_level] = match_count
#     best_match = max(desirable_matches, key = lambda x: desirable_matches[x])
#     return best_match

# def _get_flat_df(
#         df: pd.DataFrame,
#         pattern
# ):
#     matching_level = _find_matching_level(df, pattern)
#     columns = df.columns.get_level_values(matching_level)
#     recolumned_df = pd.DataFrame(
#         df.values,
#         columns
#     )
#     return recolumned_df
