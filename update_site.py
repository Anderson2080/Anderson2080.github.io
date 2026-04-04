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
        "https://www.solidot.org/index.rss" 
    ]
    news_items = []
    for url in feeds:
        try:
            parsed = feedparser.parse(url)
            # 每个源取前 5 条，总共 10 条，避免喂给AI太多
            for entry in parsed.entries[:5]:
                # 关键修复1：强行截断摘要长度，只取前300个字符
                raw_summary = entry.summary if hasattr(entry, 'summary') else ""
                # 关键修复2：用正则洗掉摘要里自带的乱七八糟的 HTML 代码，大幅节省 Token
                clean_summary = re.sub(r'<[^>]+>', '', raw_summary)
                short_summary = clean_summary[:300]
                
                news_items.append(f"标题：{entry.title}\n链接：{entry.link}\n摘要：{short_summary}...")
        except Exception as e:
            continue
            
    return "\n\n".join(news_items)

def generate_radar_html(news_text):
    prompt = f"""
    你是一个名叫“芯无旁骛”的顶尖AI与芯片产业专家。请阅读以下最新资讯，完成【情报雷达】的构建任务。
    
    【核心任务】：
    你必须输出且仅输出 3 条深度情报，分别严格对应以下三个领域：
    1. AI Infra
    2. Agent
    3. 芯片前沿

    【严格执行以下逻辑】：
    1. 匹配与挑选：从提供的资讯中寻找与这三个领域最相关的 TOP 动态。
    2. 专家级评价：用极其权威、犀利、穿透商业/技术本质的语气进行点评（100字左右）。不要平铺直叙，要反共识、讲出内行门道。
    3. 兜底机制：如果今天的新闻中确实没有某个领域的直接新闻，请你动用专家的先验知识，结合行业当前最大的痛点，自己撰写一条该领域的硬核前瞻研判（此时链接可以随便配一个相关的，或者填 # ）。
    4. 重点高亮：必须在每段点评中最核心的论点/金句上，使用以下HTML标签画蓝色波浪线：
       <span class="underline decoration-wavy decoration-blue-500 underline-offset-4 font-semibold text-slate-800">这是金句</span>
    
    【输出格式要求】：
    请直接输出 3 个 <a> 标签包裹的 HTML 代码，不要带 ```html 标记，不要多余的废话。
    模板如下（请确保标签名为相应的领域名）：

    <a href="[原文链接]" target="_blank" class="block bg-slate-100/70 hover:bg-slate-100 p-6 rounded-xl transition-colors group border border-transparent hover:border-slate-200 mb-4">
        <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-blue-600 bg-blue-100 px-2.5 py-0.5 rounded uppercase tracking-wider">[此处填入：AI Infra 或 Agent 或 芯片前沿]</span>
            <span class="text-sm font-semibold text-slate-500">Top Intel</span>
        </div>
        <h4 class="text-lg font-bold text-slate-900 leading-snug group-hover:text-blue-600 transition-colors mb-3">
            [在这里写一个极具洞察力的标题]
        </h4>
        <p class="text-base text-slate-600 font-serif leading-relaxed">
            [在这里写你的权威评价，必须包含带有波浪线高亮的 span 标签]
        </p>
    </a>
    
    资讯内容如下：
    {news_text}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7 # 稍微降低一点发散度，让它更聚焦
    )
    
    result = response.choices[0].message.content
    result = re.sub(r'^```html\n?', '', result, flags=re.IGNORECASE)
    result = re.sub(r'^```\n?', '', result)
    result = re.sub(r'```$', '', result)
    
    return result.strip()

def update_html():
    print("正在大范围抓取并清理资讯(节省Token)...")
    news = get_latest_news()
    
    print("AI 专家正在构建三大领域的情报雷达...")
    new_radar_html = generate_radar_html(news)
    
    print("正在写入网页...")
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
    
    print("情报雷达三大阵地更新完毕！")

if __name__ == "__main__":
    update_html()
