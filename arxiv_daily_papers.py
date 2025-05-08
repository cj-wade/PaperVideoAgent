import arxiv
import datetime
import os
import json
from typing import List, Dict, Any

class ArxivPaperFetcher:
    def __init__(self, save_dir: str = "data"):
        """初始化ArXiv论文获取器
        
        Args:
            save_dir: 保存数据的目录
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
    def fetch_daily_papers(self, category: str = "cs.AI", max_results: int = 10) -> List[Dict[str, Any]]:
        """获取每日最新的AI领域论文
        
        Args:
            category: arXiv类别，默认为cs.AI（人工智能）
            max_results: 获取的论文数量
            
        Returns:
            包含论文信息的字典列表
        """
        # 获取今天的日期
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 构建查询
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = []
        for result in search.results():
            # 提取论文信息
            paper_info = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "affiliations": [getattr(author, 'affiliation', '') for author in result.authors],
                "summary": result.summary,
                "published": result.published.strftime("%Y-%m-%d"),
                "updated": result.updated.strftime("%Y-%m-%d"),
                "arxiv_id": result.entry_id.split('/')[-1],
                "pdf_url": result.pdf_url,
                "primary_category": result.primary_category,
                "categories": result.categories
            }
            papers.append(paper_info)
        
        # 保存到JSON文件
        output_file = os.path.join(self.save_dir, f"arxiv_papers_{today}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
            
        print(f"已获取{len(papers)}篇论文并保存到 {output_file}")
        return papers

if __name__ == "__main__":
    fetcher = ArxivPaperFetcher()
    papers = fetcher.fetch_daily_papers()
    print(f"获取了 {len(papers)} 篇论文") 