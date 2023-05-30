import streamlit as st
import json
import os
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, GPTSimpleKeywordTableIndex
from llama_index import StorageContext, load_index_from_storage
import my_key
from llama_index import ServiceContext, LLMPredictor
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
import glob

os.environ['OPENAI_API_KEY'] = my_key.get_key()

st.markdown("""
    <style>
    .block-container {
        padding-top: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Load keywords from the JSON file
def load_keywords():
    try:
        with open('key.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

keywords = load_keywords()
# Read JSON file
with open('result.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Language selection in the sidebar
language = st.sidebar.radio("语言 / language", ('中文', 'English'))

st.title("Lucas's 金融分析GPT" if language == '中文' else "Lucas's Financial Analysis GPT")
st.image("https://media.discordapp.net/ephemeral-attachments/1108030524204789820/1113129692514484336/CodingLucas_This_is_a_sexy_and_hot_financial_analyst_working_in_46e94ec8-d1e8-4831-8dbc-75298b6ff569.png?width=2580&height=866", use_column_width=True)

# Use radio buttons in the sidebar as tabs
tab_labels = ['每日快报', '我的聚焦', '自助分析'] if language == '中文' else ['Daily Report', 'My Focus', 'Self-service Analysis']
tab = st.sidebar.radio("请选择", tab_labels)

# Run button
run_button = st.sidebar.button("立刻分析" if language == '中文' else "Run Analysis")

if tab == tab_labels[0]:  # 每日快报 / Daily Report
    st.header("每日快报" if language == '中文' else "Daily Report")

    st.subheader("1.每日资讯" if language == '中文' else "1.Daily News")
    # Get the first five file names in the folder
    news_files = sorted(glob.glob("data/*.txt"))[:5]
    # Initialize an empty string to store all news and corresponding time
    news_info = ''

    for news_file in news_files:
        with open(news_file, "r", encoding="utf-8") as file:
            title = file.readline().strip().replace('新闻标题：', '')
            title = title[:35] + '...' if len(title) > 35 else title
            time = file.readline().strip().replace('发布时间:', '')
            time = time[:5]
            news_info += f"【{time}】{title}\n\n"

    st.info(news_info)

    st.subheader("2.热门推荐" if language == '中文' else "2.Hot Recommendations")
    if "热门推荐" in results:
        st.success(results["热门推荐"])

    st.subheader("3.行业发现" if language == '中文' else "3.Industry Discovery")
    if "行业发现" in results:
        st.warning(results["行业发现"])

elif tab == tab_labels[1]:  # 我的聚焦 / My Focus
    st.header("我的聚焦" if language == '中文' else "My Focus")
    selected_keywords = st.multiselect("追踪关键词" if language == '中文' else "Track Keywords", keywords, default=keywords)
    for keyword in selected_keywords:
        st.write(keyword)
        if f'{keyword}_key' in results:
            st.info(results[f'{keyword}_key'])

elif tab == tab_labels[2]:  # 自助分析 / Self-service Analysis
    st.header("自助分析" if language == '中文' else "Self-service Analysis")
    query_text = st.text_input("请输入你的问题" if language == '中文' else "Enter your question")
    query_button = st.button("查询" if language == '中文' else "Query")

    if query_button:
        if query_text:
            llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=2500)
            llm_predictor = LLMPredictor(llm=llm)
            service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
            storage_context_30 = StorageContext.from_defaults(persist_dir="./30_day_news_index")
            index_30 = load_index_from_storage(storage_context_30, service_context=service_context)

            query_engine = index_30.as_query_engine()
            response = query_engine.query("假设你现在是一个10年经验的高级金融分析师，请回答：" + query_text)
            st.write(response)
        else:
            st.warning("请输入你的问题！" if language == '中文' else "Please enter your question!")

if run_button:
    llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=2500)
    llm_predictor = LLMPredictor(llm=llm)
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    storage_context_24 = StorageContext.from_defaults(persist_dir="./24_news_index")
    index_24 = load_index_from_storage(storage_context_24, service_context=service_context)
    storage_context_30 = StorageContext.from_defaults(persist_dir="./30_day_news_index")
    index_30 = load_index_from_storage(storage_context_30, service_context=service_context)

    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()

    total_steps = len(keywords) if tab == tab_labels[1] else 2
    current_step = 0

    if tab == tab_labels[0]:  # 每日快报 / Daily Report
        query_engine = index_24.as_query_engine()

        status_text.text("正在分析: 热门推荐" if language == '中文' else "Analyzing: Hot Recommendations")
        response1 = query_engine.query("假设你现在是一个10年经验的高级金融分析师，从新闻内容中，请列举若干涨幅较大的股票/基金/板块/公司，（提供股票或者基金代码，或者相关公司名称），并分别给出关注原因，每个股票和基金单独一段，不需要开头和结尾总结")
        current_step += 1
        progress_bar.progress(current_step / total_steps)

        status_text.text("正在分析: 行业发现" if language == '中文' else "Analyzing: Industry Discovery")
        response2 = query_engine.query("假设你现在是一个10年经验的高级金融分析师，从新闻内容中，请列举若干涨幅/下降较大行业（提供相关股票或者基金代码，或者相关公司名称），并分别给出关注原因，每个行业一段，不需要开头和结尾总结")
        current_step += 1
        progress_bar.progress(current_step / total_steps)

        results["热门推荐"] = str(response1)
        results["行业发现"] = str(response2)

    elif tab == tab_labels[1]:  # 我的聚焦 / My Focus
        query_engine = index_30.as_query_engine()
        for keyword in keywords:
            status_text.text(f"正在分析: {keyword}" if language == '中文' else f"Analyzing: {keyword}")
            response_key = query_engine.query(f"假设你现在是一个10年经验的高级金融分析师，请结合新闻内容中，分析当前{keyword}的情况，并对其趋势发展、影响情况进行陈述分析，用{language}回答，如果文中不含有相关信息，则返回“未找到”或者“not found”")
            results[f'{keyword}_key'] = str(response_key)
            current_step += 1
            progress_bar.progress(current_step / total_steps)

    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f)

    progress_bar.empty()
    status_text.text("Analysis Completed!" if language == '中文' else "分析完成！")
