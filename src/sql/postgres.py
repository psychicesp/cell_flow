#%%
# Standard Library
import os

# Global
from sqlalchemy import create_engine

# Local
from .credentials import *

engine = create_engine(f"postgresql://{user}:{password}@{portal}:{port}/{database_name}")
# %%