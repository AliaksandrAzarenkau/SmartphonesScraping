import pandas as pd


def get_os_statistics(os_list):
    pd_data = pd.Series(os_list)
    os_counts = pd_data.value_counts()

    return os_counts
