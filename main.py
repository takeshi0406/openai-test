import os

import openai

# APIキーの設定
openai.api_key = os.environ["OPENAI_API_KEY"]


response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "世界的な評判について教えて"},
        {"role": "user", "content": "世界的な評判について教えて"},
        {"role": "user", "content": "世界的な評判について教えて"},
    ],
)
print(response.choices[0]["message"]["content"].strip())