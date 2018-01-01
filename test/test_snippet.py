# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""
import datasources
import entities.news
import functions.snippet
import test
import utils.utils


class SnippetTest(test.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_gen_snippet(self):
        news_text = "常用标点符号用法简表\n一、基本定义\n　　句子，前后都有停顿，并带有一定的句调，表示相对完整的意义。句子前后或中间的停顿，在口头语言中，表现出来就是时间间隔，在书面语言中，就用标点符号来表示。一般来说，汉语中的句子分以下几种：\n　　陈述句：用来说明事实的句子。\n　　祈使句：用来要求听话人做某件事情的句子。\n　　疑问句：用来提出问题的句子。\n　　感叹句：用来抒发某种强烈感情的句子。\n　　复句、分句：意思上有密切联系的小句子组织在一起构成一个大句子。这样的大句子叫复句，复句中的每个小句子叫分句。\n　　构成句子的语言单位是词语，即词和短语（词组）。词即最小的能独立运用的语言单位。短语，即由两个或两个以上的词按一定的语法规则组成的表达一定意义的语言单位，也叫词组。\n　　标点符号是书面语言的有机组成部分，是书面语言不可缺少的辅助工具。它帮助人们确切地表达思想感情和理解书面语言。"
        news_sample = entities.news.NewsPlain(content=utils.utils.remove_wild_char(news_text), abstract="ABSTRACT")
        session = datasources.get_db().create_session()
        news_sample = datasources.get_db().upsert_news_or_news_list(session, news_sample)
        snippet = functions.snippet.gen_snippet(session, ["陈述", "事实"], news_id=news_sample.id, length=20)
        self.assertIn("陈述句：用来说明事实的句子。", snippet)
        snippet = functions.snippet.gen_snippet(session, ["组织", "复句"], news_id=news_sample.id, length=50)
        self.assertIn("组织在一起构成一个大句子。这样的大句子叫复句", snippet)
        snippet = functions.snippet.gen_snippet(session, ["猫", "复句"], news_id=news_sample.id, length=20)
        self.assertIn("复句、分句：", snippet)
        snippet = functions.snippet.gen_snippet(session, ["常用", "简表"], news_id=news_sample.id, length=20)
        self.assertIn("常用标点符号用法简表", snippet)
        snippet = functions.snippet.gen_snippet(session, ["常用", "简表"], news_id=news_sample.id, length=5)
        self.assertIn("常用", snippet)
        snippet = functions.snippet.gen_snippet(session, ["猫"], news_id=news_sample.id, length=5)
        self.assertEqual("ABSTR", snippet)
        datasources.get_db().close_session(session)

