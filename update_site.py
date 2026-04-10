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

def get_latest_news(days=7):
    news_items = []
    days_ago = datetime.now() - timedelta(days=days)
    for url in SOURCES:
        try:
            parsed = feedparser.parse(url)
            valid_entries = 0
            for entry in parsed.entries:
                if valid_entries >= 3: break
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    entry_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    if entry_date < days_ago: continue
                
                raw_summary = entry.summary if hasattr(entry, 'summary') else ""
                clean_summary = re.sub(r'<[^>]+>', '', raw_summary)
                news_items.append(f"标题：{entry.title}\n链接：{entry.link}\n摘要：{clean_summary[:250]}")
                valid_entries += 1
        except: continue
    return "\n\n".join(news_items)

# ========== 1. 每日雷达生成引擎 ==========
def generate_radar_html(news_text):
    prompt = f"""
    你叫“芯无旁骛”，顶尖AI与芯片产业专家。阅读以下科技资讯，输出3条深度情报：1. AI Infra  2. Agent  3. 芯片前沿。
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
        cards += f"""<div class="mb-12"><div class="inline-block bg-slate-900 text-white text-sm font-bold px-4 py-1.5 rounded-full mb-6 shadow-sm">{item['date']}</div><div class="space-y-4">{item['html']}</div></div>"""
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>过往情报雷达 | 芯无旁骛 Neural Silicon</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Lora:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet"><style>body {{ background-color: #F8FAFC; color: #0F172A; font-family: 'Inter', sans-serif; }} </style></head><body class="antialiased"><nav class="max-w-4xl mx-auto px-6 py-8 flex justify-between items-center"><div class="text-xl font-black tracking-tight flex items-center gap-2"><div class="w-8 h-8 bg-emerald-500 flex items-center justify-center text-white text-sm font-bold rounded-md">雷</div><span>情报雷达 Archive</span></div><a href="index.html" class="text-sm font-bold text-slate-500 hover:text-emerald-600 transition-colors uppercase tracking-widest">返回主页</a></nav><main class="max-w-4xl mx-auto px-6 pb-20 pt-10"><h1 class="text-4xl md:text-5xl font-black mb-12 tracking-tight text-slate-900">Radar <span class="text-slate-300 font-light mx-2">/</span> <span class="font-serif italic text-emerald-600 text-3xl md:text-4xl">过往情报集</span></h1><div>{cards}</div></main></body></html>"""
    with open('radar_archive.html', 'w', encoding='utf-8') as f: f.write(html)


# ========== 2. 每周巨献：SemiAnalysis 级硬核长文生成引擎 ==========
def generate_deep_dive_data(news_text):
    prompt = f"""
    你是全球最顶尖、最毒舌的 AI Infra 与芯片架构首席分析师（你的对标人物是 SemiAnalysis 的 Dylan Patel）。
    你只为全球顶级对冲基金、芯片巨头的高管撰写价值 10 万美元的内部付费研报。
    
    请从以下【本周全球最新资讯】中提取一个切入点，写一篇极度硬核、信息密度爆炸、反共识的深度研判长文。

    【极度严苛的写作纪律（违背任何一条都是失败）】：
    1. 绝对不要解释什么是大模型、什么是芯片等基础概念！你的读者是资深专家。直接切入最底层的物理、算力和商业逻辑。
    2. 必须大量使用并深入分析具体的硬核指标，例如：
       - 硬件层：SRAM 单元面积与漏电流、HBM3e/HBM4的堆叠良率与TSV成本、TSMC CoWoS-L/SOIC 封装产能瓶颈、NVLink 与 NVSwitch 的拓扑局限、PCIe 6.0 协议开销、RoCEv2 与 InfiniBand 的尾部延迟。
       - 算法层：KV Cache 的 PagedAttention 显存碎片化、Test-Time Compute (System 2) 带来的 TTFT 暴增、MoE 路由坍塌、FP8/FP4 的精度墙。
    3. 语气要高傲、冷酷、一针见血，必须指出目前市场上某个被过度炒作的谎言（例如某巨头的 PPT 性能），并用技术逻辑无情反驳。
    4. 篇幅必须极度宏大，信息量爆炸，达到大模型单次输出的物理极限（至少4000字以上的高密度干货）。

    【排版与配图强制要求】：
    在 [CONTENT] 中，必须分为 4 到 5 个深不可测的专业章节。
    必须在合适的章节中插入这 3 张架构/硬件配图（并为每张图配上一句专业的图注）：
    图1：<figure class="my-10"><img src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1200&auto=format&fit=crop" class="w-full h-[28rem] object-cover rounded-2xl shadow-lg border border-slate-200"><figcaption class="text-center text-sm text-slate-500 mt-3 font-medium">Exhibit 1: 硅基底层的物理极限与封装演进路径</figcaption></figure>
    图2：<figure class="my-10"><img src="https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=1200&auto=format&fit=crop" class="w-full h-[28rem] object-cover rounded-2xl shadow-lg border border-slate-200"><figcaption class="text-center text-sm text-slate-500 mt-3 font-medium">Exhibit 2: 异构计算网络拓扑与多智能体状态路由</figcaption></figure>
    图3：<figure class="my-10"><img src="https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1200&auto=format&fit=crop" class="w-full h-[28rem] object-cover rounded-2xl shadow-lg border border-slate-200"><figcaption class="text-center text-sm text-slate-500 mt-3 font-medium">Exhibit 3: 下一代 AI Infra 的集群互联架构</figcaption></figure>

    【强制输出格式】：
    [TITLE] (写一个充满火药味和专业度的极客标题) [/TITLE]

    [HOME_SUMMARY] (用于主页的导语，400字。必须包含 <ul> 列表，列出本文揭露的3个残酷真相，制造极强的付费阅读感。) [/HOME_SUMMARY]

    [CONTENT] (纯 HTML 排版，多用 <h3>, <p>, <blockquote>, 表格 <table> 等标签提升专业感。内容必须深不可测！) [/CONTENT]

    【本周全球资讯参考】：
    {news_text}
    """
    
    # 彻底解除封印：将 max_tokens 开到最大，并调低 temperature 让它聚焦于硬核逻辑而非发散文学
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role": "user", "content": prompt}], 
        temperature=0.3, 
        max_tokens=8000
    )
    text = response.choices[0].message.content
    try:
        title = re.search(r'\[TITLE\](.*?)\[/TITLE\]', text, re.S).group(1).strip()
        home_summary = re.search(r'\[HOME_SUMMARY\](.*?)\[/HOME_SUMMARY\]', text, re.S).group(1).strip()
        content = re.search(r'\[CONTENT\](.*?)\[/CONTENT\]', text, re.S).group(1).strip()
        return title, home_summary, content
    except Exception as e:
        print("长文解析失败，请检查模型输出。")
        return "顶级研判正在推演中", "<p>算力正在集中...</p>", "<p>生成失败，请重试。</p>"

def build_article_page(title, date_str, content):
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title} | 芯无旁骛 Neural Silicon</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Lora:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet"><style>body {{ background-color: #F8FAFC; color: #0F172A; }} .font-serif p {{ margin-bottom: 2rem; line-height: 1.9; font-size: 1.15rem; }} .font-serif h3 {{ font-family: 'Inter', sans-serif; font-size: 1.85rem; font-weight: 900; margin-top: 4rem; margin-bottom: 1.5rem; color: #0F172A; letter-spacing: -0.025em; border-bottom: 2px solid #E2E8F0; padding-bottom: 0.5rem; }} .font-serif blockquote {{ border-left: 4px solid #2563EB; padding-left: 1.5rem; font-style: italic; color: #334155; background: #F1F5F9; padding: 2rem; border-radius: 0.5rem; margin-top: 2.5rem; margin-bottom: 2.5rem; font-size: 1.15rem; font-family: 'Inter', sans-serif; }} .font-serif ul {{ list-style-type: disc; padding-left: 1.5rem; margin-bottom: 2rem; font-size: 1.15rem; line-height: 1.8; }} .font-serif li {{ margin-bottom: 0.75rem; }}</style></head><body class="antialiased selection:bg-blue-200 selection:text-blue-900"><nav class="max-w-4xl mx-auto px-6 py-8"><a href="../index.html" class="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-blue-600 transition-colors uppercase tracking-widest">← 返回主页 Home</a></nav><main class="max-w-4xl mx-auto px-6 pb-24"><div class="mb-14 border-b border-slate-200 pb-10"><div class="text-blue-600 font-bold tracking-widest uppercase mb-6 text-sm flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-blue-600"></span> 全球智库级研判 Deep Dive</div><h1 class="text-4xl md:text-5xl lg:text-6xl font-black leading-[1.2] tracking-tight text-slate-900 mb-8">{title}</h1><div class="text-slate-500 font-bold text-sm uppercase tracking-widest">{date_str}</div></div><article class="font-serif text-slate-800">{content}</article></main></body></html>"""
    return html

# ========== 3. 全局调度逻辑 ==========
def update_html():
    timestamp_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    display_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    today_url = f"articles/{timestamp_id}.html"
    
    # 【每日任务】：获取新闻并更新右侧雷达
    print(">> 正在抓取资讯并更新每日雷达...")
    news = get_latest_news(days=7) # 获取7天内的新闻供雷达和长文共同参考
    raw_radar_html = generate_radar_html(news)
    
    radar_archive_file = 'radar_archive.json'
    radar_list = []
    if os.path.exists(radar_archive_file):
        with open(radar_archive_file, 'r', encoding='utf-8') as f: radar_list = json.load(f)
    radar_list = [x for x in radar_list if x['date'][:10] != display_date[:10]] # 避免同一天重复
    radar_list.append({"date": display_date[:10], "html": raw_radar_html})
    with open(radar_archive_file, 'w', encoding='utf-8') as f: json.dump(radar_list, f, ensure_ascii=False, indent=2)
    build_radar_archive_page(radar_list)

    radar_with_link_html = raw_radar_html + """
    <div class="mt-6 pt-5 border-t border-slate-200">
        <a href="radar_archive.html" class="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-emerald-600 transition-colors uppercase tracking-widest">
            过往情报雷达 Archive 
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
        </a>
    </div>
    """

    # 【每周任务】：严格控制长文更新频率 (间隔必须大于等于 6 天)
    print(">> 正在检查长文冷却时间...")
    archive_file = 'archive.json'
    archive_list = []
    if os.path.exists(archive_file):
        with open(archive_file, 'r', encoding='utf-8') as f: archive_list = json.load(f)
        
    should_update_deep_dive = False
    if len(archive_list) == 0:
        should_update_deep_dive = True
    else:
        last_date_str = archive_list[0]['date'][:10]
        last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
        days_since_last = (datetime.now() - last_date).days
        if days_since_last >= 6:
            should_update_deep_dive = True

    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 更新雷达 (每日必须更新)
    html_content = re.sub(r'<!-- RADAR_START -->.*?<!-- RADAR_END -->', f'<!-- RADAR_START -->\n{radar_with_link_html}\n<!-- RADAR_END -->', html_content, flags=re.DOTALL)

    # 只有冷却结束，才调用大模型耗时写万字长文
    if should_update_deep_dive:
        print(">> 冷却完毕！正在令 AI 构思撰写本周极度硬核长文（耗时较长请等待）...")
        title, home_summary, content = generate_deep_dive_data(news) # 动态传入本周新闻找灵感
        
        os.makedirs('articles', exist_ok=True)
        with open(today_url, 'w', encoding='utf-8') as f:
            f.write(build_article_page(title, display_date, content))
            
        archive_list.insert(0, {"id": timestamp_id, "date": display_date, "title": title, "excerpt": home_summary, "url": today_url})
        with open(archive_file, 'w', encoding='utf-8') as f: json.dump(archive_list, f, ensure_ascii=False, indent=2)
        
        # 提取过往文章列表
        past_articles_html = ""
        past_list = archive_list[1:5]
        if past_list:
            li_items = "".join([f'<li class="border-b border-slate-100 last:border-0 pb-3 last:pb-0"><a href="{item["url"]}" class="group block"><div class="text-sm md:text-base font-bold text-slate-700 group-hover:text-blue-600 transition-colors leading-snug mb-1">{item["title"]}</div><div class="text-xs text-slate-400 font-medium uppercase tracking-wider">{item["date"]}</div></a></li>' for item in past_list])
            past_articles_html = f'<div class="mt-8 pt-8 border-t border-slate-200"><h4 class="text-sm font-black text-slate-400 uppercase tracking-widest mb-5 flex items-center gap-2"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>过往深度研判 ARCHIVE</h4><ul class="space-y-4">{li_items}</ul></div>'

        new_deep_dive_html = f"""
        <!-- DEEP_DIVES_START -->
        <article class="group relative bg-white border border-slate-200 p-8 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 pr-0 md:pr-8 flex flex-col h-full">
            <div class="flex items-center justify-between mb-6">
                <div class="flex items-center gap-3 text-xs font-bold uppercase tracking-wider">
                    <span class="text-white bg-blue-600 px-3 py-1.5 rounded-md shadow-sm">核心研判 / Tech Thesis</span>
                    <span class="text-slate-500">{display_date}</span>
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
        html_content = re.sub(r'<!-- DEEP_DIVES_START -->.*?<!-- DEEP_DIVES_END -->', new_deep_dive_html, html_content, flags=re.DOTALL)
        print(">> 本周极度硬核长文注入完毕！")
    else:
        print(">> 左侧长文尚未度过 7 天冷却期，保持不变，仅完成右侧雷达更新。")
    
    with open('index.html', 'w', encoding='utf-8') as f: f.write(html_content)
    print("✅ 系统全自动升级完成！")

if __name__ == "__main__":
    update_html()
