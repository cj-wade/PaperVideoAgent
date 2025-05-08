import os
import json
import subprocess
from typing import Dict, Any, List
import datetime
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

class VideoGenerator:
    def __init__(self, save_dir: str = "videos"):
        """初始化视频生成器
        
        Args:
            save_dir: 保存视频的目录
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def generate_video(self, poster_path: str, audio_path: str, paper_id: str, index: int) -> str:
        """为单篇论文生成视频
        
        Args:
            poster_path: 海报文件路径
            audio_path: 音频文件路径
            paper_id: 论文ID
            index: 论文索引
            
        Returns:
            视频文件路径
        """
        output_path = os.path.join(self.save_dir, f"video_{index+1:02d}_{paper_id}.mp4")
        
        try:
            # 加载音频和图像
            audio_clip = AudioFileClip(audio_path)
            image_clip = ImageClip(poster_path).set_duration(audio_clip.duration)
            
            # 将图像和音频合成视频
            video_clip = image_clip.set_audio(audio_clip)
            
            # 导出视频
            video_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            print(f"已为论文 {paper_id} 生成视频: {output_path}")
            return output_path
        
        except Exception as e:
            print(f"生成视频失败: {e}")
            return None
    
    def combine_videos(self, video_paths: List[str]) -> str:
        """将多个视频合并为一个
        
        Args:
            video_paths: 视频文件路径列表
            
        Returns:
            合并后的视频文件路径
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        output_path = os.path.join(self.save_dir, f"daily_arxiv_report_{today}.mp4")
        
        try:
            # 使用FFmpeg合并视频
            # 创建一个包含所有视频文件的列表文件
            list_file_path = os.path.join(self.save_dir, "video_list.txt")
            with open(list_file_path, 'w', encoding='utf-8') as f:
                for video_path in video_paths:
                    if os.path.exists(video_path):
                        f.write(f"file '{os.path.abspath(video_path)}'\n")
            
            # 使用FFmpeg合并视频
            subprocess.run([
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file_path,
                '-c', 'copy',
                output_path
            ], check=True)
            
            # 删除临时文件
            os.remove(list_file_path)
            
            print(f"已生成每日视频报告: {output_path}")
            return output_path
        
        except Exception as e:
            print(f"合并视频失败: {e}")
            
            # 尝试使用moviepy作为备用方案
            try:
                clips = []
                for video_path in video_paths:
                    if os.path.exists(video_path):
                        from moviepy.editor import VideoFileClip
                        clip = VideoFileClip(video_path)
                        clips.append(clip)
                
                if clips:
                    final_clip = concatenate_videoclips(clips)
                    final_clip.write_videofile(
                        output_path,
                        fps=24,
                        codec='libx264',
                        audio_codec='aac'
                    )
                    print(f"已使用备用方法生成每日视频报告: {output_path}")
                    return output_path
            except Exception as e2:
                print(f"备用方法合并视频也失败: {e2}")
            
            return None

if __name__ == "__main__":
    # 测试视频生成
    generator = VideoGenerator()
    
    # 测试单个视频生成
    poster_path = "posters/poster_01_2304.12345.png"
    audio_path = "audios/audio_01_2304.12345.wav"
    
    # 如果测试文件不存在，创建一个
    if not os.path.exists(poster_path):
        from PIL import Image, ImageDraw
        os.makedirs(os.path.dirname(poster_path), exist_ok=True)
        img = Image.new('RGB', (512, 768), color=(240, 248, 255))
        draw = ImageDraw.Draw(img)
        draw.text((20, 30), "测试海报", fill=(0, 0, 0))
        img.save(poster_path)
    
    if not os.path.exists(audio_path):
        import numpy as np
        import soundfile as sf
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        sample_rate = 24000
        duration = 5  # 5秒
        silence = np.zeros(sample_rate * duration)
        sf.write(audio_path, silence, sample_rate)
    
    video_path = generator.generate_video(poster_path, audio_path, "2304.12345", 0)
    print(f"生成的视频: {video_path}") 