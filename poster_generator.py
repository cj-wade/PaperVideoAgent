import os
import requests
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import torch
from diffusers import StableDiffusionPipeline
from typing import Dict, Any

class PosterGenerator:
    def __init__(self, save_dir: str = "posters", use_local_model: bool = True, model_id: str = "stabilityai/stable-diffusion-2-1"):
        """初始化海报生成器
        
        Args:
            save_dir: 保存海报的目录
            use_local_model: 是否使用本地模型
            model_id: 使用的模型ID
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        if use_local_model:
            # 加载本地Stable Diffusion模型
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16
            )
            if torch.cuda.is_available():
                self.pipe = self.pipe.to("cuda")
        else:
            self.pipe = None
    
    def generate_poster(self, paper: Dict[str, Any], index: int) -> str:
        """为论文生成海报
        
        Args:
            paper: 论文信息字典
            index: 论文索引
            
        Returns:
            海报文件路径
        """
        # 提取论文标题和摘要的前100个字符作为提示
        title = paper["title"]
        summary_short = paper["summary"][:100]
        
        # 构建提示词
        prompt = f"Academic poster for AI research paper titled '{title}'. {summary_short}"
        
        # 生成图像
        if self.pipe is not None:
            # 使用本地模型生成
            image = self.pipe(prompt, height=768, width=512).images[0]
        else:
            # 使用简单的模板生成
            image = self._create_template_poster(paper)
        
        # 保存图像
        output_path = os.path.join(self.save_dir, f"poster_{index+1:02d}_{paper['arxiv_id']}.png")
        image.save(output_path)
        
        print(f"已为论文 {paper['arxiv_id']} 生成海报: {output_path}")
        return output_path
    
    def _create_template_poster(self, paper: Dict[str, Any]) -> Image.Image:
        """创建一个简单的模板海报
        
        Args:
            paper: 论文信息
            
        Returns:
            生成的海报图像
        """
        # 创建一个空白图像
        img = Image.new('RGB', (512, 768), color=(240, 248, 255))
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            title_font = ImageFont.truetype("arial.ttf", 24)
            author_font = ImageFont.truetype("arial.ttf", 18)
            text_font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
            title_font = ImageFont.load_default()
            author_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # 绘制标题
        title = paper["title"]
        draw.text((20, 30), title, fill=(0, 0, 0), font=title_font)
        
        # 绘制作者
        authors = ", ".join(paper["authors"])
        draw.text((20, 100), f"Authors: {authors}", fill=(0, 0, 0), font=author_font)
        
        # 绘制摘要
        summary = paper["summary"]
        # 简单的文本换行
        words = summary.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 60:  # 简单的换行
                lines.append(" ".join(current_line[:-1]))
                current_line = [current_line[-1]]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        y_position = 150
        for line in lines[:20]:  # 限制行数
            draw.text((20, y_position), line, fill=(0, 0, 0), font=text_font)
            y_position += 25
        
        return img

if __name__ == "__main__":
    import json
    
    # 加载示例论文数据
    with open("data/arxiv_papers_2023-05-01.json", "r") as f:
        papers = json.load(f)
    
    # 测试海报生成
    generator = PosterGenerator(use_local_model=False)  # 使用模板方式
    for i, paper in enumerate(papers[:2]):  # 只测试前两篇
        poster_path = generator.generate_poster(paper, i)
        print(f"生成的海报: {poster_path}") 