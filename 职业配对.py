import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings

warnings.filterwarnings('ignore')

# 配置参数
CONFIG = {
    "data_path": "1.xlsx",  # Excel文件路径
    "sheet_name": "sheet",  # 工作表名称
    "model_name": "paraphrase-multilingual-MiniLM-L12-v2",  # 语义模型
    "threshold": 0.65,  # 相似度阈值
    "top_n": 5  # 返回结果数量
}


def load_and_preprocess_data():
    """加载并预处理Excel数据"""
    # 读取Excel文件
    df = pd.read_excel(CONFIG["data_path"], sheet_name=CONFIG["sheet_name"])

    # 数据清洗
    df = df.dropna(subset=["专业名称", "职业名称"])  # 删除关键字段缺失的行
    df["专业名称"] = df["专业名称"].str.strip()  # 去除前后空格
    df["职业名称"] = df["职业名称"].str.strip()

    # 提取唯一专业和职业信息
    unique_majors = df["专业名称"].unique().tolist()
    unique_jobs = df[["职业名称", "院校类型"]].drop_duplicates().to_dict('records')

    return df, unique_majors, unique_jobs


def initialize_model():
    """初始化语义模型"""
    return SentenceTransformer(CONFIG["model_name"])


def generate_embeddings(model, unique_majors, unique_jobs):
    """生成文本嵌入向量"""
    # 专业名称嵌入
    major_embeddings = model.encode(unique_majors)

    # 职业信息嵌入（组合职业名称和院校类型）
    job_texts = [f"{job['职业名称']} ({job['院校类型']})" for job in unique_jobs]
    job_embeddings = model.encode(job_texts)

    return major_embeddings, job_embeddings, job_texts


class CareerRecommender:
    def __init__(self, df, model, major_embeddings, job_embeddings, unique_jobs, job_texts):
        self.df = df
        self.model = model
        self.major_embeddings = major_embeddings
        self.job_embeddings = job_embeddings
        self.unique_jobs = unique_jobs
        self.job_texts = job_texts
        self.major_to_job_map = df.groupby('专业名称')['职业名称'].unique().to_dict()

    def exact_match(self, major):
        """精确匹配查询"""
        return self.major_to_job_map.get(major, [])

    def semantic_search(self, input_major, school_type=None):
        """语义相似度搜索"""
        input_embed = self.model.encode([input_major])[0]
        similarities = cosine_similarity([input_embed], self.job_embeddings)[0]

        results = []
        for idx, score in enumerate(similarities):
            job_info = self.unique_jobs[idx]
            if score < CONFIG["threshold"]:
                continue
            if school_type and job_info["院校类型"] != school_type:
                continue
            results.append((self.job_texts[idx], score))

        return sorted(results, key=lambda x: -x[1])[:CONFIG["top_n"]]

    def recommend(self, major, school_type=None):
        """综合推荐入口"""
        # 精确匹配优先
        exact_jobs = self.exact_match(major)
        if len(exact_jobs) > 0:
            return [("精确匹配", job, "100%") for job in exact_jobs]

        # 语义匹配
        semantic_results = self.semantic_search(major, school_type)
        return [("语义匹配", res[0], f"{res[1]:.0%}") for res in semantic_results]


def main():
    # 初始化系统
    print("正在加载数据与模型...")
    df, unique_majors, unique_jobs = load_and_preprocess_data()
    model = initialize_model()
    major_embeddings, job_embeddings, job_texts = generate_embeddings(model, unique_majors, unique_jobs)
    recommender = CareerRecommender(df, model, major_embeddings, job_embeddings, unique_jobs, job_texts)

    # 交互界面
    print("\n=== 智能岗位推荐系统 ===")
    print(f"已加载数据量：{len(df)}条")
    print(f"支持专业数量：{len(unique_majors)}个")
    print(f"支持岗位数量：{len(unique_jobs)}种\n")

    while True:
        major = input("请输入查询的专业名称（输入q退出）: ").strip()
        if major.lower() == 'q':
            break

        school_type = input("请选择院校类型筛选（可选：职教专科/职教中职/普通本科/技工院校等，直接回车跳过）: ").strip()

        print("\n推荐结果：")
        recommendations = recommender.recommend(major, school_type)

        if not recommendations:
            print("⚠️ 未找到相关岗位推荐")
            continue

        for i, (match_type, job, score) in enumerate(recommendations, 1):
            print(f"{i}. [{match_type}] {job} ({score})")
        print("-" * 50)


if __name__ == "__main__":
    main()