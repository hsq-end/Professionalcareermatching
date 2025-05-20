该Python代码实现了一个基于语义相似度的专业-岗位推荐系统，主要功能如下：
load_and_preprocess_data：加载Excel数据并清洗，提取唯一专业和职业信息。
initialize_model：加载用于语义嵌入的预训练模型（如Sentence-BERT）。
generate_embeddings：为专业名称和职业信息生成向量表示。
main：构建推荐器并提供交互式命令行界面，用户输入专业名称后返回匹配的职业推荐。
This Python code implements a professional-job recommendation system based on semantic similarity, with the following main functions: load_and_preprocess_data: load and clean Excel data, extracting unique major and job information. initialize_model: load a pre-trained model for semantic embedding (such as Sentence-BERT). generate_embeddings: generate vector representations for major names and job information. main: build the recommender and provide an interactive command line interface, returning matching job recommendations after the user inputs the major name.
