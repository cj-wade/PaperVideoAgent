import os
import json
import datetime
import argparse
from typing import List, Dict, Any

from arxiv_daily_papers import ArxivPaperFetcher
from poster_generator import PosterGenerator
from script_generator import ScriptGenerator
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator

def main():
    parser = argparse.ArgumentParser(description="AI论文每日视频播报生成器")
    parser.add_argument("--category", type=str, default="cs.AI", help="arXiv类别")
    parser.add_argument("--max_papers", type=int, default=10, help="获取的论文数量")
    parser.add_argument("--use_local_model", action="store_true", help="使用本地Stable Diffusion模型")
    parser.add_argument("--output_dir", type=str, default="output", help="输出目录")
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 设置各模块的保存目录
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    data_dir = os.path.join(args.output_dir, "data")
    poster_dir = os.path.join(args.output_dir, "posters", today)
    script_dir = os.path.join(args.output_dir, "scripts", today)
    audio_dir = os.path.join(args.output_dir, "audios", today)
    video_dir = os.path.join(args.output_dir, "videos", today)
    
    # 1. 获取arXiv论文
    print("正在获取arXiv论文...")
    fetcher = ArxivPaperFetcher(save_dir=data_dir)
    papers = fetcher.fetch_daily_papers(category=args.category, max_results=args.max_papers)
    
    if not papers:
        print("未获取到论文，程序退出")
        return
    
    # 2. 为每篇论文生成海报
    print("\n正在生成论文海报...")
    poster_generator = PosterGenerator(save_dir=poster_dir, use_local_model=args.use_local_model)
    poster_paths = []
    
    for i, paper in enumerate(papers):
        poster_path = poster_generator.generate_poster(paper, i)
        poster_paths.append(poster_path)
    
    # 3. 为每篇论文生成文案
    print("\n正在生成播报文案...")
    script_generator = ScriptGenerator(save_dir=script_dir)
    script_paths = []
    
    for i, paper in enumerate(papers):
        script_path = script_generator.generate_script(paper, i)
        script_paths.append(script_path)
    
    # 4. 为每篇文案生成语音
    print("\n正在生成播报语音...")
    voice_generator = VoiceGenerator(save_dir=audio_dir)
    audio_paths = []
    
    for i, paper in enumerate(papers):
        audio_path = voice_generator.generate_voice(script_paths[i], paper["arxiv_id"], i)
        audio_paths.append(audio_path)
    
    # 5. 为每篇论文生成视频
    print("\n正在生成单篇论文视频...")
    video_generator = VideoGenerator(save_dir=video_dir)
    video_paths = []
    
    for i, paper in enumerate(papers):
        video_path = video_generator.generate_video(poster_paths[i], audio_paths[i], paper["arxiv_id"], i)
        if video_path:
            video_paths.append(video_path)
    
    # 6. 合并所有视频
    if video_paths:
        print("\n正在合并所有视频...")
        final_video = video_generator.combine_videos(video_paths)
        if final_video:
            print(f"\n视频生成完成! 最终视频: {final_video}")
        else:
            print("\n合并视频失败!")
    else:
        print("\n没有生成任何视频!")

if __name__ == "__main__":
    main() 