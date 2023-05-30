from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader,GPTSimpleKeywordTableIndex
from llama_index import StorageContext, load_index_from_storage
import my_key,os
from llama_index import ServiceContext, LLMPredictor
# from langchain.llms import OpenAI
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
os.environ['OPENAI_API_KEY'] = my_key.get_key()

# 设置LLM,
llm = ChatOpenAI(model = "gpt-3.5-turbo", max_tokens=2500)
llm_predictor = LLMPredictor(llm=llm)
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
# 生成本地index
documents = SimpleDirectoryReader('data').load_data()
index = GPTVectorStoreIndex.from_documents(documents,service_context=service_context)
index.storage_context.persist('30_day_news_index')

# #  读取本地向量index
# storage_context = StorageContext.from_defaults(persist_dir="./GPT_index")
# index = load_index_from_storage(storage_context,service_context= service_context)

# # 提出问题
# query_engine = index.as_query_engine()
# response = query_engine.query("结合这些新闻，请分析值得关注的潜在股票和投资方向")
# print(str(response))
