import os
import re
import feedparser
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("AI_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def get_latest_news():
    feeds = [
        "https://36kr.com/feed", 
        # 你未来可以在这里加更多 RSS
    ]
    news_items = []
    for url in feeds:
        parsed = feedparser.parse(url)
        for entry in parsed.entries[:3]:
            # 【升级点1】：现在不仅抓取标题和摘要，还把原文链接抓下来了
            news_items.append(f"标题：{entry.title}\n链接：{entry.link}\n摘要：{entry.summary}")
    return "\n\n".join(news_items)

def generate_radar_html(news_text):
    # 【升级点2】：全面升级提示词，要求字数更长、语气更犀利、自动加波浪线和原文链接
    prompt = f"""
    你是一个名叫“芯无旁骛”的顶尖AI与芯片产业专家。请阅读以下最新资讯，挑选出2条最能影响行业格局的，改写成硬核、专业的深度短评。
    
    【严格要求】：
    1. 语气必须权威、犀利、反共识。不要做简单的总结，要直击技术底层逻辑或商业本质，甚至带有批判性。
    2. 每条点评的字数在 100-150 字左右，内容要丰满。
    3. 必须在点评中最核心的论点或金句上添加波浪线高亮。使用以下 HTML 标签包裹需要高亮的文字：
       <span class="underline decoration-wavy decoration-blue-500 underline-offset-4 font-semibold text-slate-800">这是重点金句</span>
    4. 请直接输出 HTML 代码，不要带任何 Markdown 标记（如 ```html ）。格式必须完全符合以下模板：

    <a href="[此处填入真实的原新闻链接]" target="_blank" class="block bg-slate-100/70 hover:bg-slate-100 p-6 rounded-xl transition-colors group border border-transparent hover:border-slate-200 mb-4">
        <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-blue-600 bg-blue-100 px-2.5 py-0.5 rounded uppercase tracking-wider">深度评析</span>
            <span class="text-sm font-semibold text-slate-500">今日前沿</span>
        </div>
        <h4 class="text-lg font-bold text-slate-900 leading-snug group-hover:text-blue-600 transition-colors mb-3">
            [在这里写一个极具洞察力的标题]
        </h4>
        <p class="text-base text-slate-600 font-serif leading-relaxed">
            [在这里写你的深度点评。记得用 span 标签给核心金句加波浪线]
        </p>
    </a>
    
    资讯内容如下：
    {news_text}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 增加一层防护：清理大模型偶尔会带上的 ```html 标记
    result = response.choices[0].message.content
    result = re.sub(r'^```html\n?', '', result, flags=re.IGNORECASE)
    result = re.sub(r'^```\n?', '', result)
    result = re.sub(r'```$', '', result)
    
    return result.strip()

def update_html():
    print("正在抓取新闻及链接...")
    news = get_latest_news()
    
    print("正在呼叫 Groq AI 进行深度思考并排版...")
    new_radar_html = generate_radar_html(news)
    
    print("正在替换网页内容...")
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_content = re.sub(
        r'<!-- RADAR_START -->.*?<!-- RADAR_END -->',
        f'<!-- RADAR_START -->\n{new_radar_html}\n<!-- RADAR_END -->',
        html_content,
        flags=re.DOTALL
    )
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("网站更新成功！")

if __name__ == "__main__":
    update_html()
