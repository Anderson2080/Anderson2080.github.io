import os
import re
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
                if valid_entries >= 2:
                    break
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    entry_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    if entry_date < seven_days_ago:
                        continue
                
                raw_summary = entry.summary if hasattr(entry, 'summary') else ""
                clean_summary = re.sub(r'<[^>]+>', '', raw_summary)
                short_summary = clean_summary[:200]
                news_items.append(f"原新闻标题：{entry.title}\n链接：{entry.link}\n摘要：{short_summary}...")
                valid_entries += 1
        except Exception as e:
            continue
            
    return "\n\n".join(news_items)

# ================= 核心引擎 1：情报雷达生成器 =================
def generate_radar_html(news_text):
    prompt = f"""
    你是一个名叫“芯无旁骛”的顶尖AI与芯片产业专家。阅读以下【最近7天内】的全球权威科技源资讯，输出 3 条深度情报，严格对应：
    1. AI Infra  2. Agent  3. 芯片前沿

    要求：
    1. 标题必须一字不差使用英文原标题，不可翻译。
    2. 点评必须用中文，100字左右，极其权威犀利。
    3. 在每段中文点评的核心金句上，使用该标签高亮：<span class="underline decoration-wavy decoration-blue-500 underline-offset-4 font-semibold text-slate-800">金句内容</span>
    4. 直接输出 3 个 <a> 标签的 HTML 代码，不要任何 Markdown 标记。

    HTML 模板：
    <a href="[原文链接]" target="_blank" class="block bg-slate-100/70 hover:bg-slate-100 p-6 rounded-xl transition-colors group border border-transparent hover:border-slate-200 mb-4">
        <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-blue-600 bg-blue-100 px-2.5 py-0.5 rounded uppercase tracking-wider">[领域名]</span>
            <span class="text-sm font-semibold text-slate-500">今日前沿</span>
        </div>
        <h4 class="text-lg font-bold text-slate-900 leading-snug group-hover:text-blue-600 transition-colors mb-3">
            [英文原标题]
        </h4>
        <p class="text-base text-slate-600 font-serif leading-relaxed">
            [中文深度点评，含波浪线高亮]
        </p>
    </a>
    
    资讯内容：
    {news_text}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    result = re.sub(r'^```(html)?\n?|\n?```$', '', response.choices[0].message.content, flags=re.IGNORECASE)
    return result.strip()

# ================= 核心引擎 2：深度研判长文生成器 =================
def generate_deep_dive_html():
    prompt = """
    你是一个名叫“芯无旁骛”的世界顶级AI Infra与芯片创新专家。请撰写一篇极其硬核、权威、图文并茂的战略研判文章。
    
    【核心背景与主题设定】：
    以“GTC 2026 对 AI Infra 发展趋势的颠覆”为主题。
    请在文章中深刻探讨以下前沿技术趋势（展现你顶级的先验知识）：
    1. NVIDIA下一代Rubin架构对算力格局的改变。
    2. 硅光互联（CPO）与NVLink规模化如何打破通信“内存墙”。
    3. AI Infra 正在从“支持预训练的大吞吐量”向“支持海量Agent高并发与KV Cache状态管理的极速响应”全面倾斜。

    【输出要求】：
    1. 不要客套废话，行文需具有强烈的牵引性、数据支撑感和压迫感，令人醍醐灌顶。
    2. 直接输出以下 HTML 代码，并将其中的 [此处填入...] 替换为你撰写的雄文。
    3. 不要输出任何 Markdown 标记（如 ```html），只输出纯正的 HTML。

    【HTML 严格排版模板】：
    <article class="group cursor-pointer pr-0 md:pr-4">
        <div class="flex items-center justify-between mb-5 border-b border-slate-200 pb-4">
            <div class="flex items-center gap-3 text-xs font-bold uppercase tracking-wider">
                <span class="text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-md shadow-sm">首席研判 / Tech Thesis</span>
                <span class="text-slate-500">MAY 2026</span>
            </div>
        </div>

        <h4 class="text-3xl md:text-4xl lg:text-[2.5rem] font-black text-slate-900 mb-6 group-hover:text-blue-600 transition-colors duration-300 leading-[1.15] tracking-tight">
            [此处填入：极具震撼力的主标题，例如“GTC 2026 纪元：Rubin 架构与 Agentic Infra 的光电跃迁”]
        </h4>

        <div class="relative mb-8">
            <div class="absolute left-0 top-0 bottom-0 w-1.5 bg-blue-600 rounded-l-md"></div>
            <p class="text-lg md:text-xl text-slate-700 font-serif leading-relaxed pl-6 bg-gradient-to-r from-slate-50 to-transparent py-4 pr-4">
                [此处填入：核心摘要导语，高度浓缩 GTC 2026 带来的范式转移，100字左右]
            </p>
        </div>

        <div class="overflow-hidden rounded-2xl mb-10 shadow-md ring-1 ring-slate-900/5">
            <img src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1200&auto=format&fit=crop" alt="AI Silicon" class="w-full h-64 md:h-[22rem] object-cover transform group-hover:scale-105 transition-transform duration-1000 ease-in-out">
        </div>

        <div class="space-y-8 text-slate-700 font-serif text-lg leading-[1.8]">
            <div>
                <h3 class="text-2xl font-black text-slate-900 font-sans mb-3 tracking-tight flex items-center gap-2">
                    <span class="text-blue-600">01 /</span> [此处填入：小标题1，关于Rubin架构与算力重构]
                </h3>
                <p class="mb-4">[此处填入：深度分析正文内容]</p>
                <p>[此处填入：深度分析正文内容，并使用 <span class="underline decoration-wavy decoration-emerald-500 underline-offset-4 font-semibold text-slate-800">高亮标签包裹核心金句</span>]</p>
            </div>

            <div>
                <h3 class="text-2xl font-black text-slate-900 font-sans mb-3 tracking-tight flex items-center gap-2">
                    <span class="text-blue-600">02 /</span> [此处填入：小标题2，关于硅光互联打破内存墙]
                </h3>
                <p class="mb-4">[此处填入：深度分析正文内容，提供强逻辑或数据感]</p>
                <p>[此处填入：深度分析正文内容]</p>
            </div>

            <blockquote class="bg-[#0F172A] text-slate-300 p-6 md:p-8 rounded-2xl my-8 shadow-xl font-sans">
                <p class="text-xl font-medium leading-relaxed text-white">
                    “[此处填入：一句极具行业穿透力的断言引言]”
                </p>
            </blockquote>

            <div>
                <h3 class="text-2xl font-black text-slate-900 font-sans mb-3 tracking-tight flex items-center gap-2">
                    <span class="text-blue-600">03 /</span> [此处填入：小标题3，关于面向 Agent 的 Infra 重构]
                </h3>
                <p class="mb-4">[此处填入：分析如何从预训练吞吐量向Agent高并发和KV Cache管理转移]</p>
            </div>

            <div class="mt-10 bg-blue-50/50 border border-blue-100 rounded-2xl p-6 md:p-8">
                <h4 class="text-sm font-black text-blue-600 uppercase tracking-widest mb-4">Strategic Verdict / 战略研判</h4>
                <ul class="space-y-4 font-sans text-slate-800">
                    <li class="flex items-start gap-3">
                        <svg class="w-6 h-6 text-blue-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <span><strong>致技术开发者：</strong>[此处填入：前瞻建议]</span>
                    </li>
                    <li class="flex items-start gap-3">
                        <svg class="w-6 h-6 text-blue-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <span><strong>致创新创业者：</strong>[此处填入：前瞻建议]</span>
                    </li>
                    <li class="flex items-start gap-3">
                        <svg class="w-6 h-6 text-blue-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <span><strong>致前沿投资人：</strong>[此处填入：前瞻建议]</span>
                    </li>
                </ul>
            </div>
        </div>
    </article>
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6 # 稍微提高发散度，让长文更有想象力和文采
    )
    result = re.sub(r'^```(html)?\n?|\n?```$', '', response.choices[0].message.content, flags=re.IGNORECASE)
    return result.strip()

# ================= 网页融合器 =================
def update_html():
    print("【步骤1】正在扫略过去7天内的全球顶级科技源...")
    news = get_latest_news()
    
    print("【步骤2】AI首席分析师正在生成情报雷达(右侧)...")
    new_radar_html = generate_radar_html(news)

    print("【步骤3】AI首席架构师正在撰写GTC2026深度长文(左侧)...")
    new_deep_dive_html = generate_deep_dive_html()
    
    print("【步骤4】正在执行自动化排版注入网页...")
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 替换情报雷达
    html_content = re.sub(
        r'<!-- RADAR_START -->.*?<!-- RADAR_END -->',
        f'<!-- RADAR_START -->\n{new_radar_html}\n<!-- RADAR_END -->',
        html_content,
        flags=re.DOTALL
    )

    # 替换深度研判长文
    html_content = re.sub(
        r'<!-- DEEP_DIVES_START -->.*?<!-- DEEP_DIVES_END -->',
        f'<!-- DEEP_DIVES_START -->\n{new_deep_dive_html}\n<!-- DEEP_DIVES_END -->',
        html_content,
        flags=re.DOTALL
    )
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ 网站双轨（雷达+长文）全自动更新完毕！")

if __name__ == "__main__":
    update_html()
