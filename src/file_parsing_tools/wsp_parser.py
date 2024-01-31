# Global Imports
import xmltodict

# ----------------------------------------
# Supporting Functions
# ----------------------------------------

def _wsp_to_dict(wsp_location: str) -> dict:
    # Opens workspace file and converts to dictionary

    with open(wsp_location, 'r') as wsp_file:
        wsp_dict = xmltodict.parse(wsp_file.read())
    return wsp_dict

def _sanitize_file_name(file_name: str):
    # We may use unquote for this in future

    clean_file_name = file_name.split('/')[-1]
    clean_file_name = clean_file_name.replace('%20', ' ')
    return clean_file_name

# ----------------------------------------
# Main
# ----------------------------------------

def samples_from_wsp(wsp_location: str)-> list:
    """
    Unpacks .wsp xml file as a dict and extracts a list of associated samples

    Args:
        wsp_location: string of a valid file name/location of the .wsp file.

    Returns:
        A list of sample file names (not with location)
    """
    wsp_dict = _wsp_to_dict(wsp_location)
    sample_list = wsp_dict['Workspace']['SampleList']['Sample']
    sample_names = [x['DataSet']['@uri'] for x in sample_list]
    clean_sample_names = [_sanitize_file_name(x) for x in sample_names]
    return clean_sample_names


