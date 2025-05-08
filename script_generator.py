import os
import json
from typing import Dict, Any, List
import ollama

class ScriptGenerator:
    def __init__(self, model_name: str = "qwen3", save_dir: str = "scripts"):
        """初始化文案生成器
        
        Args:
            model_name: 使用的Ollama模型名称
            save_dir: 保存文案的目录
        """
        self.model_name = model_name
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def generate_script(self, paper: Dict[str, Any], index: int) -> str:
        """为论文生成播报文案
        
        Args:
            paper: 论文信息字典
            index: 论文索引
            
        Returns:
            文案文件路径
        """
        # 提取论文信息
        title = paper["title"]
        authors = ", ".join(paper["authors"])
        affiliations = ", ".join([a for a in paper["affiliations"] if a])
        summary = paper["summary"]
        
        # 构建提示词
        prompt = f"""
        请为以下AI研究论文生成一段简短的播报文案，语言要通俗易懂，适合视频播报：
        
        标题: {title}
        作者: {authors}
        单位: {affiliations}
        摘要: {summary}
        
        要求:
        1. 文案长度控制在300字以内
        2. 先介绍论文标题和作者单位
        3. 然后简明扼要地介绍论文的主要内容和创新点
        4. 语言要生动有趣，适合视频播报
        5. 只输出文案内容，不要有其他格式或说明
        """
        
        # 调用Ollama生成文案
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ])
            script = response["message"]["content"].strip()
        except Exception as e:
            print(f"调用Ollama模型失败: {e}")
            # 备用方案：生成一个简单的模板文案
            script = f"""今天为大家介绍一篇来自{affiliations}的研究论文，标题是《{title}》。
            
这篇论文由{authors}等研究者共同完成。论文主要内容是{summary[:150]}...

这项研究对人工智能领域具有重要意义，期待未来有更多相关工作。"""
        
        # 保存文案
        output_path = os.path.join(self.save_dir, f"script_{index+1:02d}_{paper['arxiv_id']}.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"已为论文 {paper['arxiv_id']} 生成文案: {output_path}")
        return output_path

if __name__ == "__main__":
    # 加载示例论文数据
    with open("data/arxiv_papers_2023-05-01.json", "r") as f:
        papers = json.load(f)
    
    # 测试文案生成
    generator = ScriptGenerator()
    for i, paper in enumerate(papers[:2]):  # 只测试前两篇
        script_path = generator.generate_script(paper, i)
        print(f"生成的文案: {script_path}") 