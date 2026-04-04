import os
import re
import feedparser
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("AI_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# 全球顶级前沿信源
SOURCES = [
    "https://www.semianalysis.com/feed",
    "https://www.servethehome.com/feed/", 
    "https://semiengineering.com/feed/",
    "https://www.theinformation.com/feed",
    "https://rss.arxiv.org/rss/cs.AI",
    "https://techcrunch.com/category/artificial-intelligence/feed/"
]

def get_latest_news():
    news_items = []
    for url in SOURCES:
        try:
            parsed = feedparser.parse(url)
            # 每个源取前2条核心动态
            for entry in parsed.entries[:2]:
                raw_summary = entry.summary if hasattr(entry, 'summary') else ""
                clean_summary = re.sub(r'<[^>]+>', '', raw_summary)
                short_summary = clean_summary[:200]
                
                news_items.append(f"原新闻标题：{entry.title}\n链接：{entry.link}\n摘要：{short_summary}...")
        except Exception as e:
            continue
            
    return "\n\n".join(news_items)

def generate_radar_html(news_text):
    prompt = f"""
    你是一个名叫“芯无旁骛”的顶尖AI与芯片产业专家。请阅读以下从全球权威科技源抓取的最新资讯，完成【情报雷达】的构建任务。
    
    【核心任务】：
    你必须输出且仅输出 3 条深度情报，分别严格对应以下三个领域：
    1. AI Infra
    2. Agent
    3. 芯片前沿

    【严格执行以下逻辑】：
    1. 匹配挑选：从资讯中寻找与这三个领域最相关的 TOP 动态。
    2. 保持原汁原味的英文标题：卡片上的标题必须【一字不差地使用原英文新闻标题，绝对不要翻译成中文】，绝对不要瞎编！
    3. 专家级中文评价：虽然标题是英文，但你的深度点评【必须全部用中文撰写】。语气极其权威、犀利、穿透商业/技术本质（100字左右）。
    4. 兜底机制：如果没找到某领域的资讯，动用你的先验知识写一条该领域的硬核前瞻研判（链接填 # ）。
    5. 重点高亮：必须在每段的中文点评中，找出最核心的论点/金句，使用以下HTML标签画蓝色波浪线：
       <span class="underline decoration-wavy decoration-blue-500 underline-offset-4 font-semibold text-slate-800">这是金句</span>
    
    【输出格式要求】：
    请直接输出 3 个 <a> 标签包裹的 HTML 代码，不要带 ```html 标记，不要多余的废话。
    模板如下（请确保标签名为相应的领域名，副标题为“今日前沿”）：

    <a href="[原文链接]" target="_blank" class="block bg-slate-100/70 hover:bg-slate-100 p-6 rounded-xl transition-colors group border border-transparent hover:border-slate-200 mb-4">
        <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-blue-600 bg-blue-100 px-2.5 py-0.5 rounded uppercase tracking-wider">[此处填入：AI Infra 或 Agent 或 芯片前沿]</span>
            <span class="text-sm font-semibold text-slate-500">今日前沿</span>
        </div>
        <h4 class="text-lg font-bold text-slate-900 leading-snug group-hover:text-blue-600 transition-colors mb-3">
            [此处必须填入：原汁原味的原新闻标题（不翻译）]
        </h4>
        <p class="text-base text-slate-600 font-serif leading-relaxed">
            [在这里写你的权威中文评价，必须包含带有波浪线高亮的 span 标签]
        </p>
    </a>
    
    全球抓取资讯内容如下：
    {news_text}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    result = response.choices[0].message.content
    result = re.sub(r'^```html\n?', '', result, flags=re.IGNORECASE)
    result = re.sub(r'^```\n?', '', result)
    result = re.sub(r'```$', '', result)
    
    return result.strip()

def update_html():
    print("正在扫略全球顶级科技源(SemiAnalysis, arXiv等)...")
    news = get_latest_news()
    
    print("AI专家正在进行跨语种研判与排版...")
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
    
    print("硬核情报雷达更新完毕！")

if __name__ == "__main__":
    update_html()
