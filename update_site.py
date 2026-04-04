import os
import re
import feedparser
from openai import OpenAI

# 1. 配置你的 API (这里已经替换成了 Groq 的地址)
client = OpenAI(
    api_key=os.environ.get("AI_API_KEY"), # 密码变量名保持不变，稍后在 GitHub 里配置 Groq 的 Key
    base_url="https://api.groq.com/openai/v1" # <--- 修改点 1：替换了 API 请求地址
)

# 2. 获取资讯源 (这里以 36氪 为例，你可以自己换)
def get_latest_news():
    feeds = [
        "https://36kr.com/feed", 
        # 可以添加更多 RSS 链接
    ]
    news_items = []
    for url in feeds:
        parsed = feedparser.parse(url)
        for entry in parsed.entries[:3]: # 取前3条
            news_items.append(f"标题：{entry.title}\n摘要：{entry.summary}")
    return "\n\n".join(news_items)

# 3. 让 AI 生成“情报雷达”的 HTML 代码
def generate_radar_html(news_text):
    prompt = f"""
    你是一个名叫“芯无旁骛”的AI与芯片产业专家。请阅读以下最新资讯，挑选出2条最有价值的，改写成硬核、专业的短评。
    请直接输出 HTML 代码，不要任何 Markdown 标记，格式必须完全符合以下模板：
    <a href="#" class="block bg-slate-100/70 hover:bg-slate-100 p-6 rounded-xl transition-colors group border border-transparent hover:border-slate-200 mb-4">
        <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-blue-600 bg-blue-100 px-2.5 py-0.5 rounded uppercase tracking-wider">短评</span>
            <span class="text-sm font-semibold text-slate-500">今日前沿</span>
        </div>
        <h4 class="text-lg font-bold text-slate-900 leading-snug group-hover:text-blue-600 transition-colors mb-2">
            [在这里写一个吸引人的标题]
        </h4>
        <p class="text-base text-slate-600 line-clamp-2 font-serif leading-relaxed">
            [在这里写一段一针见血的点评，不要超过50个字]
        </p>
    </a>
    
    资讯内容如下：
    {news_text}
    """
    
    # <--- 修改点 2：替换成了 Llama 3.3 70B 模型
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 4. 替换 HTML 文件内容
def update_html():
    # 获取新闻并生成HTML
    print("正在抓取新闻...")
    news = get_latest_news()
    
    print("正在呼叫 Groq AI 思考...")
    new_radar_html = generate_radar_html(news)
    
    print("正在替换网页内容...")
    # 读取原始 index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 使用正则表达式替换占位符之间的内容
    html_content = re.sub(
        r'<!-- RADAR_START -->.*?<!-- RADAR_END -->',
        f'<!-- RADAR_START -->\n{new_radar_html}\n<!-- RADAR_END -->',
        html_content,
        flags=re.DOTALL
    )
    
    # 写回文件
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("网站更新成功！")

if __name__ == "__main__":
    update_html()