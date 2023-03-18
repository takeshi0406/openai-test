import json
import pytz
import requests
import feedparser
from retry import retry
from datetime import datetime, timedelta
from slack_sdk.webhook import WebhookClient
from newschatbot.lib.settings import settings
from newschatbot.arxiv_client import ArxivClient
from newschatbot.openai_client import StatelessClient
from newschatbot.valueobjects import YukkuriConversations, Article, MessageBuilder


JST = pytz.timezone('Asia/Tokyo')


class MainClass:
    def __init__(self):
        self.yukkurizer = Yukkurizer()
        self.crawler = RssCrawler(url="https://ledge.ai/feed")
        # self.crawler = RssCrawler(url="https://www.lifull.blog/rss")
        self.slack = SlackClient(settings.slack_endpoint)
        self.arxiv = ArxivClient()

    def run(self):
        yesterday = datetime.now(JST).date() - timedelta(days=1)

        articles = self.arxiv.fetch() + self.crawler.fetch()
        for a in articles:
            if a.published.astimezone(JST).date() != yesterday:
                continue

            m = MessageBuilder(
                article=a,
                conversations=self.yukkurizer.summarize(a.content),
            )
            self.slack.send_message(m.to_message())


class Yukkurizer:
    def __init__(self):
        self.summarizer = StatelessClient("""
        次のメッセージで送られる記事を中学生向けに日本語で要約してください。
        ただし、次の条件を守ってください。

        * floorplanは「間取り」と翻訳する
        """)
        self.yukkurizer = StatelessClient("""
        次のメッセージで送られる内容をゆっくり霊夢とゆっくり魔理沙の対話形式のjson形式に加工してください。
        対話はそれぞれ2文以内で、教育番組で子供向けに刺さる内容に仕上げてください。

        ゆっくり魔理沙(yukkuri_marisa)は次のようなパーソナリティです。
        
        * 最初の一言目は、ゆっくり魔理沙の質問文*ではない*、要約の一言コメントから始めてください
        * あらゆる分野に深い知識を持っている
        * ゆっくり霊夢の質問に対してゆっくり魔理沙がわかりやすく答える
        * ゆっくり魔理沙は「だぜ」「するぜ」「したぜ」という語尾の多い男勝りの口調
        
        ゆっくり霊夢(yukkuri_reimu)は次のようなパーソナリティです。
        
        * 好奇心旺盛で、記事のわからない点について積極的に質問をする
        * 「だわ」「なの？」「かしら？」「わよ」「よね」という語尾の多い女性っぽい口調
        
        二人は仲の良い友人なのでくだけた口調でしゃべります。
        一つのコメントは20文字以内に収めてください。


        返答の内容をそのままプログラムで利用したいため、必ず次のようなjson形式に加工してください。
        ```json
        {
            "conversations": [
                {"speaker": "yukkuri_marisa", "content": "ゆっくり魔理沙が「つまり〜なんだぜ」と要約をする"}, 
                {"speaker": "yukkuri_reimu", "content": "それについてゆっくり霊夢が質問する"},
                {"speaker": "yukkuri_reimu", "content": "ゆっくり魔理沙が回答をする"},
                {"speaker": "yukkuri_marisa", "content": "ゆっくり霊夢がコメントする"}
            ]
        }
        ```
        """)

    def summarize(self, article: str) -> YukkuriConversations:
        summarized = self.summarizer.request(article)
        print(f"ok:f{summarized[0:20]}...")
        return self._yukkurize(summarized)

    @retry(tries=3)
    def _yukkurize(self, content: str) -> YukkuriConversations:
        res = self.yukkurizer.request(content)
        return YukkuriConversations(**json.loads(res))


class RssCrawler:
    def __init__(self, url: str):
        self.url = url

    def fetch(self) -> list[Article]:
        results = []
        feed = feedparser.parse(self.url)
        for entry in feed.entries:
            results.append(
                Article(
                    title=entry.title,
                    url=entry.link,
                    published=datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z'),
                    content="".join(x.value for x in entry.content)
                    # content=requests.get(entry.link).text.replace(" ", "")[0:10000]
                )
            )
        return results


class SlackClient:
    def __init__(self, endpoint: str):
        self.webhook = WebhookClient(endpoint)

    def send_message(self, message: str):
        self.webhook.send(text=message)


if __name__ == "__main__":
    MainClass().run()
