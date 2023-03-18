from __future__ import annotations
import datetime
from pydantic import BaseModel
from typing import Literal 


class Article(BaseModel):
    title: str
    url: str
    published: datetime.datetime # Fri, 17 Mar 2023 10:54:48 +0000
    content: str


class YukkuriConversations(BaseModel):
    conversations: list[YukkuriConversation]

    def to_message(self) -> str:
        return "\n".join(x.to_message() for x in self.conversations)


class YukkuriConversation(BaseModel):
    speaker: Literal["yukkuri_reimu", "yukkuri_marisa"]
    content: str

    def to_message(self) -> str:
        if self.speaker == "yukkuri_reimu":
            return f":left_side_balloon_without_tail: {self.content} :right_side_balloon_with_tail: :yukkuri_reimu:"
        else:
            return f":yukkuri_marisa: :left_side_balloon_with_tail: {self.content} :right_side_balloon_without_tail:"


class MessageBuilder(BaseModel):
    article: Article
    conversations: YukkuriConversations

    def to_message(self) -> str:
        return "\n".join([
            f"*{self.article.title}*",
            self.article.url,
            "",
            self.conversations.to_message(),
        ])


YukkuriConversations.update_forward_refs()