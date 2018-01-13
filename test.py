import test
import datasources

datasources.get_db().recreate_all_tables()
test.runSQL()