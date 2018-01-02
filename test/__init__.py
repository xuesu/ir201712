# -*- coding:utf-8 -*-
"""
@author: xuesu

used to prepare testcase environment
"""

import unittest

import config
import datasources


class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        config.spark_config.testing = True


def runSQL():
    session = datasources.get_db().create_session()
    # Open the .sql file
    sql_file = open("dump.sql", 'r')

    # Create an empty command string
    sql_command = ''

    # Iterate over all lines in the sql file
    for line in sql_file:
        # Ignore comented lines
        if not line.startswith('--') and line.strip('\n'):
            # Append line to the command string
            sql_command += line.strip('\n')

            # If the command string ends with ';', it is a full statement
            if sql_command.endswith(';'):
                # Try to execute statemente and commit it
                try:
                    session.execute(sql_command)
                    session.commit()

                # Assert in case of error
                except Exception as e:
                    print('Ops')

                # Finally, clear command string
                finally:
                    sql_command = ''
    datasources.get_db().close_session(session)