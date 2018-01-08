import indexes
import test
import update
import api
import datasources


class SearchTest(test.TestCase):
    def setUp(self):
        # datasources.get_db().recreate_all_tables()
        test.runSQL()
        # self.app = api.app.test_client()
        # self.app.testing = True
        # print('wait...  we need to init IndexHolder...')
        # indexes.IndexHolder()

    def tearDown(self):
        pass

    def test_search(self):

        # resp = self.app.get("/search", query_string={"query": "护士 直播", "ranking-by": 1, "page": 1})
        # print('search: ', resp.data)
        print('success')



