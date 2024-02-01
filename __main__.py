# Global
import sys

# Local
# from src.sql.execute import phoenix, _the_technology
from src.data_extraction.project_parse import read_project


file_location = sys.argv[1]

read_project(file_location)
