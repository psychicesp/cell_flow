# %%
# Standard Library Imports

# Global Imports
import pandas as pd

# Local Imports
from ..sql.postgres import engine

# ----------------------------------------
# Supporting Functions
# ----------------------------------------

def _prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        if df[column].dtype.name == 'float64':
            df[column] = df[column].astype('float32')
    if 'id' in df.columns:
        df.set_index('id', inplace=True)
    elif 'event_id' in df.columns: 
        df.set_index('event_id', inplace=True)
    return df


# ----------------------------------------
# Main Function
# ----------------------------------------

def to_database(
    df: pd.DataFrame,
    table_name: str
) -> None:
    """
    Pushes DataFrame into sql
    Args: 
    df: DataFrame to be pushed to SQL
    table_name: Name of the SQL table
    """

    df = _prepare_df(df)

    # This will give an opportunity for a user to rescue an errored out process
    keep_going = True
    while keep_going:
        try:
            with engine.connect() as con:
                df.to_sql(
                    name = table_name,
                    con = con,
                    if_exists='append'
                )
            keep_going = False
        except Exception as e:
            print(e)
            response = input('Try again? Y/n')
            keep_going = response.lower() != 'n'