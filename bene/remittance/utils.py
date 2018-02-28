"""
Remittance utiltiies
"""

import datetime as dt

def date_to_path(this_date):
    return this_date.strftime(f'%Y/%Y-%m/%Y-%m-%d_%H-%M')


