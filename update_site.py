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

# ========== 生成雷达与雷达归档 ==========
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
    return re.sub(r'^```(html)?\n?|\n?最新?\n?|\n?```$', '', response.choices[0].message.content, flags=re.IGNORECASE).strip()

def build_radar_archive_page(radar_list):
    cards = ""
    for item in sorted(radar_list, key=lambda x: x['date'], reverse=True):
        cards += f"""
        <div class="mb-12">
            <div class="inline-block bg-slate-900 text-white text-sm font-bold px-4 py-1.5 rounded-full mb-6 shadow-sm">{item['date']}</div>
            <div class="space-y-4">{item['html']}</div>
        </div>
        """
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>过往情报雷达 | 芯无旁骛 Neural Silicon</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Lora:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet">
    <style>body {{ background-color: #F8FAFC; color: #0F172A; font-family: 'Inter', sans-serif; }} </style>
</head>
<body class="antialiased">
    <nav class="max-w-4xl mx-auto px-6 py-8 flex justify-between items-center">
        <div class="text-xl font-black tracking-tight flex items-center gap-2">
            <div class="w-8 h-8 bg-emerald-500 flex items-center justify-center text-white text-sm font-bold rounded-md">雷</div>
            <span>情报雷达 Archive</span>
        </div>
        <a href="index.html" class="text-sm font-bold text-slate-500 hover:text-emerald-600 transition-colors uppercase tracking-widest">返回主页</a>
    </nav>
    <main class="max-w-4xl mx-auto px-6 pb-20 pt-10">
        <h1 class="text-4xl md:text-5xl font-black mb-12 tracking-tight text-slate-900">
            Radar <span class="text-slate-300 font-light mx-2">/</span> <span class="font-serif italic text-emerald-600 text-3xl md:text-4xl">过往情报集</span>
        </h1>
        <div>{cards}</div>
    </main>
</body>
</html>"""
    with open('radar_archive.html', 'w', encoding='utf-8') as f:
        f.write(html)


# ========== 生成长文与文章归档 ==========
def generate_deep_dive_data():
    prompt = """
    你是全球顶尖的AI Infra与芯片架构专家。
    请基于最近一个月的前沿趋势（如：O1/R1引发的测试时计算爆发、KV Cache内存墙、多智能体对底层的挑战等），写一篇极其硬核、反共识的深度研判长文。

    【严苛要求】：
    1. 拒绝面面俱到！像手术刀一样剖析一个单点问题。
    2. 使用大量硬核行业词汇（SRAM、HBM3e、PagedAttention等）。
    3. 在正文 [CONTENT] 中，必须插入2到3张精美配图：
       图1 URL：https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1200&auto=format&fit=crop
       图2 URL：https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=1200&auto=format&fit=crop
       HTML格式：<img src="URL" class="w-full h-64 md:h-80 object-cover rounded-2xl my-8 shadow-sm border border-slate-200">

    【必须严格输出以下格式】：
    [TITLE]中文长标题[/TITLE]
    [HOME_SUMMARY]主页引言，约400字，留有悬念。[/HOME_SUMMARY]
    [CONTENT]HTML排版的正文内容。[/CONTENT]
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], temperature=0.5
    )
    text = response.choices[0].message.content
    try:
        title = re.search(r'\[TITLE\](.*?)\[/TITLE\]', text, re.S).group(1).strip()
        home_summary = re.search(r'\[HOME_SUMMARY\](.*?)\[/HOME_SUMMARY\]', text, re.S).group(1).strip()
        content = re.search(r'\[CONTENT\](.*?)\[/CONTENT\]', text, re.S).group(1).strip()
        return title, home_summary, content
    except:
        return "系统升级中", "深度研判文章正在加载...", "<p>生成失败，请重试。</p>"

def build_article_page(title, date_str, content):
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | 芯无旁骛 Neural Silicon</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Lora:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet">
    <style>body {{ background-color: #F8FAFC; color: #0F172A; }} .font-serif p {{ margin-bottom: 1.8rem; line-height: 1.8; font-size: 1.125rem; }} .font-serif h3 {{ font-family: 'Inter', sans-serif; font-size: 1.75rem; font-weight: 900; margin-top: 3rem; margin-bottom: 1.2rem; }} .font-serif blockquote {{ border-left: 4px solid #2563EB; padding-left: 1.5rem; font-style: italic; background: #F1F5F9; padding: 1.5rem; border-radius: 0.5rem; margin-top: 2rem; margin-bottom: 2rem; font-size: 1.125rem; font-family: 'Inter', sans-serif; }} .font-serif ul {{ list-style-type: disc; padding-left: 1.5rem; margin-bottom: 1.5rem; font-size: 1.125rem; line-height: 1.8; }} .font-serif li {{ margin-bottom: 0.5rem; }}</style>
</head>
<body class="antialiased selection:bg-blue-200 selection:text-blue-900">
    <nav class="max-w-3xl mx-auto px-6 py-8"><a href="../index.html" class="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-blue-600 transition-colors uppercase tracking-widest">← 返回主页 Home</a></nav>
    <main class="max-w-3xl mx-auto px-6 pb-24">
        <div class="mb-12 border-b border-slate-200 pb-10">
            <div class="text-blue-600 font-bold tracking-widest uppercase mb-4 text-sm flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-blue-600"></span> 首席研判 Deep Dive</div>
            <h1 class="text-3xl md:text-5xl font-black leading-[1.2] tracking-tight text-slate-900 mb-6">{title}</h1>
            <div class="text-slate-500 font-medium text-sm uppercase tracking-widest">{date_str}</div>
        </div>
        <article class="font-serif text-slate-700">{content}</article>
    </main>
</body>
</html>"""
    return html

# ========== 主更新逻辑 ==========
def update_html():
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_url = f"articles/{today_str}.html"
    
    # 1. 雷达处理
    news = get_latest_news()
    raw_radar_html = generate_radar_html(news)
    
    radar_archive_file = 'radar_archive.json'
    radar_list = []
    if os.path.exists(radar_archive_file):
        with open(radar_archive_file, 'r', encoding='utf-8') as f:
            radar_list = json.load(f)
    radar_list = [x for x in radar_list if x['date'] != today_str]
    radar_list.append({"date": today_str, "html": raw_radar_html})
    with open(radar_archive_file, 'w', encoding='utf-8') as f:
        json.dump(radar_list, f, ensure_ascii=False, indent=2)
    build_radar_archive_page(radar_list)

    # 注入雷达历史链接到主页
    radar_with_link_html = raw_radar_html + """
    <div class="mt-6 pt-5 border-t border-slate-200">
        <a href="radar_archive.html" class="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-emerald-600 transition-colors uppercase tracking-widest">
            过往情报雷达 Archive 
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
        </a>
    </div>
    """

    # 2. 长文处理
    title, home_summary, content = generate_deep_dive_data()
    os.makedirs('articles', exist_ok=True)
    with open(today_url, 'w', encoding='utf-8') as f:
        f.write(build_article_page(title, today_str, content))
        
    archive_file = 'archive.json'
    archive_list = []
    if os.path.exists(archive_file):
        with open(archive_file, 'r', encoding='utf-8') as f:
            archive_list = json.load(f)
    archive_list = [x for x in archive_list if x['date'] != today_str]
    archive_list.append({"date": today_str, "title": title, "excerpt": home_summary, "url": today_url})
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(archive_list, f, ensure_ascii=False, indent=2)

    # 生成主页左侧的过往长文标题列表 (取前4篇历史文章)
    past_articles_html = ""
    past_list = sorted([x for x in archive_list if x['date'] != today_str], key=lambda x: x['date'], reverse=True)
    if past_list:
        li_items = ""
        for item in past_list[:4]:
            li_items += f"""
            <li class="border-b border-slate-100 last:border-0 pb-3 last:pb-0">
                <a href="{item['url']}" class="group block">
                    <div class="text-sm md:text-base font-bold text-slate-700 group-hover:text-blue-600 transition-colors leading-snug mb-1">{item['title']}</div>
                    <div class="text-xs text-slate-400 font-medium uppercase tracking-wider">{item['date']}</div>
                </a>
            </li>
            """
        past_articles_html = f"""
        <div class="mt-8 pt-8 border-t border-slate-200">
            <h4 class="text-sm font-black text-slate-400 uppercase tracking-widest mb-5 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                过往深度研判 ARCHIVE
            </h4>
            <ul class="space-y-4">
                {li_items}
            </ul>
        </div>
        """

    # 3. 融合进主页
    new_deep_dive_html = f"""
    <!-- DEEP_DIVES_START -->
    <article class="group relative bg-white border border-slate-200 p-8 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 pr-0 md:pr-8 flex flex-col h-full">
        <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-3 text-xs font-bold uppercase tracking-wider">
                <span class="text-white bg-blue-600 px-3 py-1.5 rounded-md shadow-sm">核心研判 / Tech Thesis</span>
                <span class="text-slate-500">{today_str}</span>
            </div>
        </div>
        <h4 class="text-3xl md:text-[2.2rem] font-black text-slate-900 mb-6 group-hover:text-blue-600 transition-colors duration-300 leading-[1.25] tracking-tight">
            {title}
        </h4>
        <div class="text-lg text-slate-600 font-serif leading-relaxed mb-8 space-y-4 flex-grow">
            {home_summary}
        </div>
        <div class="mt-2 pt-2">
            <a href="{today_url}" class="inline-flex items-center gap-2 bg-slate-900 text-white px-8 py-3.5 rounded-xl font-bold tracking-wide hover:bg-blue-600 transition-colors duration-300">
                阅读完整深度研判 
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
            </a>
        </div>
        {past_articles_html}
    </article>
    <!-- DEEP_DIVES_END -->
    """
    
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_content = re.sub(r'<!-- RADAR_START -->.*?<!-- RADAR_END -->', f'<!-- RADAR_START -->\n{radar_with_link_html}\n<!-- RADAR_END -->', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<!-- DEEP_DIVES_START -->.*?<!-- DEEP_DIVES_END -->', new_deep_dive_html, html_content, flags=re.DOTALL)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ 系统全自动升级完成！")

if __name__ == "__main__":
    update_html()
