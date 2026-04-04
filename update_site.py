import os
import re
import json
import feedparser
import time
from datetime import datetime, timedelta
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("AI_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

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
    seven_days_ago = datetime.now() - timedelta(days=7)
    for url in SOURCES:
        try:
            parsed = feedparser.parse(url)
            valid_entries = 0
            for entry in parsed.entries:
                if valid_entries >= 2: break
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    entry_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    if entry_date < seven_days_ago: continue
                
                raw_summary = entry.summary if hasattr(entry, 'summary') else ""
                clean_summary = re.sub(r'<[^>]+>', '', raw_summary)
                news_items.append(f"标题：{entry.title}\n链接：{entry.link}\n摘要：{clean_summary[:200]}")
                valid_entries += 1
        except: continue
    return "\n\n".join(news_items)

def generate_radar_html(news_text):
    prompt = f"""
    你叫“芯无旁骛”，顶尖AI与芯片产业专家。阅读以下7天内的科技资讯，输出3条深度情报：1. AI Infra  2. Agent  3. 芯片前沿。
    要求：英文原标题一字不差，中文点评极其犀利(100字)，并在金句上加 <span class="underline decoration-wavy decoration-blue-500 underline-offset-4 font-semibold text-slate-800">高亮</span>。
    
    输出3个如下 <a> 标签的纯HTML代码：
    <a href="[原文链接]" target="_blank" class="block bg-slate-100/70 hover:bg-slate-100 p-6 rounded-xl transition-colors group border border-transparent hover:border-slate-200 mb-4">
        <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-blue-600 bg-blue-100 px-2.5 py-0.5 rounded uppercase tracking-wider">[领域名]</span>
            <span class="text-sm font-semibold text-slate-500">今日前沿</span>
        </div>
        <h4 class="text-lg font-bold text-slate-900 leading-snug group-hover:text-blue-600 transition-colors mb-3">[英文原标题]</h4>
        <p class="text-base text-slate-600 font-serif leading-relaxed">[中文深度点评]</p>
    </a>
    
    资讯内容：{news_text}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], temperature=0.3
    )
    return re.sub(r'^```(html)?\n?|\n?```$', '', response.choices[0].message.content, flags=re.IGNORECASE).strip()

def generate_deep_dive_data():
    prompt = """
    你是一个世界顶级AI Infra与芯片创新专家。请撰写一篇前沿、硬核的深度研判文章。
    主题可以聚焦于：AI Infra的发展趋势、Agent的底层逻辑、或者最新芯片架构的突破。
    
    文章要求极度深入丰富、数据支撑感强、逻辑令人醍醐灌顶。不要废话。
    
    【必须严格遵守以下输出格式，绝不能用Markdown代码块，只能输出三个标签包裹的内容】：

    [TITLE]
    这里写一个震撼的中文长标题
    [/TITLE]

    [EXCERPT]
    这里写一段200字左右的极度浓缩的核心摘要，留有悬念，吸引读者点击阅读全文。
    [/EXCERPT]

    [CONTENT]
    这里写详细的正文内容。使用HTML排版（如 <h3>, <p>, <ul>, <blockquote> 等）。要求内容极其丰富详实，分几个章节深度剖析。在核心金句上使用 <span class="font-bold text-blue-600"> 进行高亮。
    [/CONTENT]
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], temperature=0.6
    )
    text = response.choices[0].message.content
    
    try:
        title = re.search(r'\[TITLE\](.*?)\[/TITLE\]', text, re.S).group(1).strip()
        excerpt = re.search(r'\[EXCERPT\](.*?)\[/EXCERPT\]', text, re.S).group(1).strip()
        content = re.search(r'\[CONTENT\](.*?)\[/CONTENT\]', text, re.S).group(1).strip()
        return title, excerpt, content
    except:
        return "系统升级中", "深度研判文章正在赶来的路上...", "<p>生成失败，请稍后重试。</p>"

# ========== 生成独立文章页面 ==========
def build_article_page(title, date_str, content):
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | 芯无旁骛 Neural Silicon</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Lora:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet">
    <style>body {{ background-color: #F8FAFC; color: #0F172A; }} .font-serif p {{ margin-bottom: 1.5rem; line-height: 1.8; }} .font-serif h3 {{ font-family: 'Inter', sans-serif; font-size: 1.5rem; font-weight: 900; margin-top: 2.5rem; margin-bottom: 1rem; color: #0F172A; }} .font-serif blockquote {{ border-left: 4px solid #2563EB; padding-left: 1rem; font-style: italic; color: #475569; background: #F1F5F9; padding: 1rem; border-radius: 0.5rem; }}</style>
</head>
<body class="antialiased selection:bg-blue-200 selection:text-blue-900">
    <nav class="max-w-4xl mx-auto px-6 py-8">
        <a href="../index.html" class="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-blue-600 transition-colors uppercase tracking-widest">
            ← 返回主页 Home
        </a>
    </nav>
    <main class="max-w-4xl mx-auto px-6 pb-20">
        <div class="mb-10 border-b border-slate-200 pb-8">
            <div class="text-blue-600 font-bold tracking-widest uppercase mb-4 text-sm">{date_str}</div>
            <h1 class="text-3xl md:text-5xl font-black leading-tight tracking-tight text-slate-900">{title}</h1>
        </div>
        <article class="font-serif text-lg text-slate-700">
            {content}
        </article>
        <div class="mt-16 pt-8 border-t border-slate-200 text-center">
            <a href="../archive.html" class="inline-block bg-slate-900 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-600 transition-colors">浏览更多历史深度研判</a>
        </div>
    </main>
</body>
</html>"""
    return html

# ========== 生成历史归档页面 ==========
def build_archive_page(archive_list):
    cards = ""
    # 按日期倒序排列
    for item in sorted(archive_list, key=lambda x: x['date'], reverse=True):
        cards += f"""
        <a href="{item['url']}" class="block bg-white border border-slate-200 p-6 rounded-2xl hover:shadow-lg hover:border-blue-300 transition-all duration-300 mb-6 group">
            <div class="text-sm font-bold text-slate-400 mb-2 uppercase tracking-wider">{item['date']}</div>
            <h2 class="text-2xl font-black text-slate-900 group-hover:text-blue-600 transition-colors mb-3 leading-snug">{item['title']}</h2>
            <p class="text-slate-600 font-serif line-clamp-2">{item['excerpt']}</p>
        </a>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>历史文库 Archive | 芯无旁骛 Neural Silicon</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Lora:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet">
    <style>body {{ background-color: #F8FAFC; color: #0F172A; }} </style>
</head>
<body class="antialiased font-sans">
    <nav class="max-w-4xl mx-auto px-6 py-8 flex justify-between items-center">
        <div class="text-xl font-black tracking-tight flex items-center gap-2">
            <div class="w-8 h-8 bg-blue-600 flex items-center justify-center text-white text-sm font-bold rounded-md">芯</div>
            <span>Neural Silicon</span>
        </div>
        <a href="index.html" class="text-sm font-bold text-slate-500 hover:text-blue-600 transition-colors">返回主页</a>
    </nav>
    <main class="max-w-4xl mx-auto px-6 pb-20 pt-10">
        <h1 class="text-4xl md:text-5xl font-black mb-12 tracking-tight text-slate-900">
            Archive <span class="text-slate-400 font-light mx-2">/</span> <span class="font-serif italic text-blue-700 text-3xl md:text-4xl">历史文库</span>
        </h1>
        <div class="space-y-2">
            {cards}
        </div>
    </main>
</body>
</html>"""
    with open('archive.html', 'w', encoding='utf-8') as f:
        f.write(html)

# ========== 主更新逻辑 ==========
def update_html():
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_url = f"articles/{today_str}.html"
    
    print("1. 获取新闻与生成雷达...")
    news = get_latest_news()
    new_radar_html = generate_radar_html(news)

    print("2. 构思撰写深度研判长文...")
    title, excerpt, content = generate_deep_dive_data()
    
    print("3. 生成独立文章页面并保存...")
    os.makedirs('articles', exist_ok=True)
    article_html = build_article_page(title, today_str, content)
    with open(today_url, 'w', encoding='utf-8') as f:
        f.write(article_html)
        
    print("4. 更新历史数据库与归档页...")
    archive_file = 'archive.json'
    archive_list = []
    if os.path.exists(archive_file):
        with open(archive_file, 'r', encoding='utf-8') as f:
            archive_list = json.load(f)
            
    # 避免同一天重复添加
    archive_list = [x for x in archive_list if x['date'] != today_str]
    archive_list.append({
        "date": today_str,
        "title": title,
        "excerpt": excerpt,
        "url": today_url
    })
    
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(archive_list, f, ensure_ascii=False, indent=2)
        
    build_archive_page(archive_list)

    print("5. 更新主页 index.html...")
    # 主页展示的简化版卡片
    new_deep_dive_html = f"""
    <!-- DEEP_DIVES_START -->
    <article class="group relative bg-white border border-slate-200 p-8 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 pr-0 md:pr-8">
        <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-3 text-xs font-bold uppercase tracking-wider">
                <span class="text-white bg-blue-600 px-3 py-1.5 rounded-md shadow-sm">首席研判</span>
                <span class="text-slate-500">{today_str}</span>
            </div>
        </div>
        <h4 class="text-3xl md:text-4xl font-black text-slate-900 mb-6 group-hover:text-blue-600 transition-colors duration-300 leading-[1.25] tracking-tight">
            {title}
        </h4>
        <p class="text-lg text-slate-600 font-serif leading-relaxed mb-8 border-l-4 border-slate-300 pl-5">
            {excerpt}
        </p>
        <a href="{today_url}" class="inline-flex items-center gap-2 bg-slate-900 text-white px-6 py-3.5 rounded-xl font-bold tracking-wide hover:bg-blue-600 transition-colors duration-300">
            阅读完整深度研判 
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
        </a>
    </article>
    <div class="mt-10 pt-8 border-t-2 border-slate-100">
        <a href="archive.html" class="inline-flex items-center gap-2 text-lg font-black text-slate-400 hover:text-slate-800 transition-colors uppercase tracking-widest">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
            浏览历史文库与归档
        </a>
    </div>
    <!-- DEEP_DIVES_END -->
    """
    
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_content = re.sub(
        r'<!-- RADAR_START -->.*?<!-- RADAR_END -->',
        f'<!-- RADAR_START -->\n{new_radar_html}\n<!-- RADAR_END -->',
        html_content, flags=re.DOTALL
    )

    html_content = re.sub(
        r'<!-- DEEP_DIVES_START -->.*?<!-- DEEP_DIVES_END -->',
        new_deep_dive_html,
        html_content, flags=re.DOTALL
    )
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ 系统全自动升级完成！")

if __name__ == "__main__":
    update_html()
