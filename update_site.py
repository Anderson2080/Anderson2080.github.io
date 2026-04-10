import os
import re
import json
import feedparser
import time
from datetime import datetime, timedelta
from openai import OpenAI

# 💡 切换为 DeepSeek 顶级模型引擎
client = OpenAI(
    api_key=os.environ.get("AI_API_KEY"),
    base_url="https://api.deepseek.com"
)

SOURCES = [
    "https://www.semianalysis.com/feed",
    "https://www.servethehome.com/feed/", 
    "https://semiengineering.com/feed/",
    "https://www.theinformation.com/feed",
    "https://rss.arxiv.org/rss/cs.AI"
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
    你是顶尖芯片产业专家。阅读以下资讯，输出3条深度情报：1. AI Infra 2. Agent 3. 芯片前沿。
    要求：保留英文原标题。中文点评极度犀利(100字)，绝不使用废话。在核心论点加 <span class="underline decoration-wavy decoration-blue-500 underline-offset-4 font-semibold text-slate-800">高亮</span>。
    
    输出3个 <a> 标签的纯HTML代码，模板如下：
    <a href="[链接]" target="_blank" class="block bg-slate-100/70 hover:bg-slate-100 p-6 rounded-xl transition-colors group border border-transparent hover:border-slate-200 mb-4">
        <div class="flex items-center justify-between mb-3"><span class="text-sm font-bold text-blue-600 bg-blue-100 px-2.5 py-0.5 rounded uppercase tracking-wider">[领域]</span><span class="text-sm font-semibold text-slate-500">今日前沿</span></div>
        <h4 class="text-lg font-bold text-slate-900 leading-snug group-hover:text-blue-600 transition-colors mb-3">[英文原标题]</h4>
        <p class="text-base text-slate-600 font-serif leading-relaxed">[中文点评]</p>
    </a>
    
    资讯：{news_text}
    """
    response = client.chat.completions.create(
        model="deepseek-chat", messages=[{"role": "user", "content": prompt}], temperature=0.3
    )
    return re.sub(r'^```(html)?\n?|\n?```$', '', response.choices[0].message.content, flags=re.IGNORECASE).strip()

# ========== 核心改造：DeepSeek 专属的投行研报提示词 ==========
def generate_deep_dive_data():
    prompt = """
    你现在是硅谷最顶尖的硬核架构分析师（对标 SemiAnalysis）。你需要为华尔街对冲基金写一篇价值 10 万美元的深度研报。
    主题围绕：Test-Time Compute、HBM 内存墙、硅光互联、KV Cache 碎片化 等极度前沿的物理与算力瓶颈。

    【🚨 绝对红线（违反直接判定失败）】：
    1. 彻底封杀以下 AI 废话词汇：“具体来说”、“这意味着”、“总而言之”、“不可否认”、“随着技术的发展”、“面临巨大的挑战”。
    2. 禁止使用空洞的形容词。必须用绝对的数学和物理参数说话（如：TFLOPS、GB/s、pJ/bit、mm²、微秒延迟）。
    3. 必须包含推演逻辑！比如不要只说“显存不够”，你要推演出：“在 FP8 精度下，100K 上下文的并发请求将瞬间榨干 80GB HBM3e，导致 NVLink 变成最大的拥塞节点”。

    【文章结构强制要求（按此框架输出）】：
    [TITLE] (写一个充满火药味、极具极客深度的中文长标题) [/TITLE]

    [HOME_SUMMARY] 
    (主页引言，约300字。极度冷酷地指出市场上过度炒作的谎言，并列出本文将要用硬核数据证明的核心真相，吸引阅读全文。要求排版紧凑，不要废话。) 
    [/HOME_SUMMARY]

    [CONTENT]
    (正文HTML排版。必须分3-4个极度专业的章节，如：
    <h3>一、算力账本：伪命题与物理极限</h3>
    <p>详细推演计算过程与功耗/成本分析...</p>
    <h3>二、架构解剖：为什么现有方案是纸上谈兵</h3>
    <p>剖析底层拓扑结构、SRAM面积局限等...</p>
    
    插入图片要求（必须带 <figure> 和 <figcaption>）：
    第一章末尾插入：<figure class="my-10"><img src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1200&auto=format&fit=crop" class="w-full h-[28rem] object-cover rounded-2xl shadow-lg border border-slate-200"><figcaption class="text-center text-sm text-slate-500 mt-3 font-medium">Exhibit 1: HBM3e 堆叠良率与 TSV 穿孔热密度的物理极限</figcaption></figure>
    第二章末尾插入：<figure class="my-10"><img src="https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=1200&auto=format&fit=crop" class="w-full h-[28rem] object-cover rounded-2xl shadow-lg border border-slate-200"><figcaption class="text-center text-sm text-slate-500 mt-3 font-medium">Exhibit 2: 多智能体并发下的互联拓扑拥塞模型</figcaption></figure>
    )
    [/CONTENT]
    """
    
    # 启用 DeepSeek 模型，并降低温度以确保极其理性的硬核输出
    response = client.chat.completions.create(
        model="deepseek-chat", 
        messages=[
            {"role": "system", "content": "你是一个冷酷、极度理性的半导体与AI底层架构科学家。你的文字如手术刀般精准，只谈论物理定律、数学公式和商业账本。"},
            {"role": "user", "content": prompt}
        ], 
        temperature=0.4
    )
    text = response.choices[0].message.content
    try:
        title = re.search(r'\[TITLE\](.*?)\[/TITLE\]', text, re.S).group(1).strip()
        home_summary = re.search(r'\[HOME_SUMMARY\](.*?)\[/HOME_SUMMARY\]', text, re.S).group(1).strip()
        content = re.search(r'\[CONTENT\](.*?)\[/CONTENT\]', text, re.S).group(1).strip()
        return title, home_summary, content
    except:
        return "系统升级中", "<p>算力重组中...</p>", "<p>生成失败，请重试。</p>"

def build_article_page(title, date_str, content):
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title} | 芯无旁骛 Neural Silicon</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Lora:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet"><style>body {{ background-color: #FAFAFA; color: #111827; }} .font-serif p {{ margin-bottom: 2.5rem; line-height: 2; font-size: 1.18rem; color: #374151; text-align: justify; }} .font-serif h3 {{ font-family: 'Inter', sans-serif; font-size: 1.8rem; font-weight: 900; margin-top: 4.5rem; margin-bottom: 1.8rem; color: #0F172A; letter-spacing: -0.03em; border-bottom: 2px solid #E2E8F0; padding-bottom: 0.8rem; }} .font-serif blockquote {{ border-left: 4px solid #0F172A; padding-left: 1.8rem; font-style: normal; color: #1E293B; background: #F1F5F9; padding: 2rem; border-radius: 0.5rem; margin: 3rem 0; font-size: 1.15rem; font-family: 'Inter', sans-serif; font-weight: 500; box-shadow: inset 0 2px 4px 0 rgb(0 0 0 / 0.05); }} .font-serif ul {{ list-style-type: square; padding-left: 1.5rem; margin-bottom: 2.5rem; font-size: 1.15rem; line-height: 1.9; color: #374151; }} .font-serif li {{ margin-bottom: 0.8rem; }}</style></head><body class="antialiased selection:bg-slate-900 selection:text-white"><nav class="max-w-4xl mx-auto px-6 py-10"><a href="../index.html" class="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-slate-900 transition-colors uppercase tracking-widest">← Back to Neural Silicon</a></nav><main class="max-w-4xl mx-auto px-6 pb-32"><div class="mb-16 border-b border-slate-300 pb-12"><div class="text-slate-900 font-bold tracking-widest uppercase mb-6 text-sm flex items-center gap-3"><span class="w-3 h-3 bg-red-600"></span> 芯无旁骛 / 首席产业研判</div><h1 class="text-4xl md:text-5xl lg:text-[3.2rem] font-black leading-[1.2] tracking-tight text-slate-900 mb-8">{title}</h1><div class="flex items-center gap-4 border-t border-slate-200 pt-6 mt-8"><div class="w-12 h-12 bg-slate-200 rounded-full flex items-center justify-center text-xl font-bold">NS</div><div><div class="font-bold text-slate-900">Neural Silicon 智库</div><div class="text-slate-500 text-sm font-medium">{date_str} · Subscriber Exclusive</div></div></div></div><article class="font-serif text-slate-800">{content}</article></main></body></html>"""
    return html

def update_html():
    timestamp_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    display_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    today_url = f"articles/{timestamp_id}.html"
    
    news = get_latest_news()
    raw_radar_html = generate_radar_html(news)
    radar_with_link_html = raw_radar_html + """<div class="mt-6 pt-5 border-t border-slate-200"><a href="radar_archive.html" class="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-emerald-600 transition-colors uppercase tracking-widest">过往情报雷达 Archive <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg></a></div>"""

    title, home_summary, content = generate_deep_dive_data()
    os.makedirs('articles', exist_ok=True)
    with open(today_url, 'w', encoding='utf-8') as f:
        f.write(build_article_page(title, display_date, content))
        
    archive_file = 'archive.json'
    archive_list = []
    if os.path.exists(archive_file):
        with open(archive_file, 'r', encoding='utf-8') as f: archive_list = json.load(f)
            
    archive_list.insert(0, {"id": timestamp_id, "date": display_date, "title": title, "excerpt": home_summary, "url": today_url})
    with open(archive_file, 'w', encoding='utf-8') as f: json.dump(archive_list, f, ensure_ascii=False, indent=2)

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
    
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_content = re.sub(r'<!-- RADAR_START -->.*?<!-- RADAR_END -->', f'<!-- RADAR_START -->\n{radar_with_link_html}\n<!-- RADAR_END -->', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<!-- DEEP_DIVES_START -->.*?<!-- DEEP_DIVES_END -->', new_deep_dive_html, html_content, flags=re.DOTALL)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    update_html()
