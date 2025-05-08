import os
import json
import subprocess
import numpy as np
from typing import Dict, Any
import torch
import torchaudio
import soundfile as sf

class VoiceGenerator:
    def __init__(self, model_path: str = "cosyvoice2.0", save_dir: str = "audios"):
        """初始化语音合成器
        
        Args:
            model_path: CosyVoice模型路径
            save_dir: 保存音频的目录
        """
        self.model_path = model_path
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        # 尝试导入CosyVoice模块
        try:
            import cosyvoice
            self.cosyvoice = cosyvoice
            self.model_loaded = True
            print("成功加载CosyVoice模型")
        except ImportError:
            print("警告: 无法导入CosyVoice模块，将使用备用方案")
            self.model_loaded = False
    
    def generate_voice(self, script_path: str, paper_id: str, index: int) -> str:
        """为文案生成语音
        
        Args:
            script_path: 文案文件路径
            paper_id: 论文ID
            index: 论文索引
            
        Returns:
            音频文件路径
        """
        # 读取文案
        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()
        
        output_path = os.path.join(self.save_dir, f"audio_{index+1:02d}_{paper_id}.wav")
        
        if self.model_loaded:
            try:
                # 使用CosyVoice生成语音
                # 注意：以下代码需要根据实际的CosyVoice API进行调整
                audio = self.cosyvoice.synthesize(
                    text=script,
                    speaker_id=0,  # 默认说话人
                    speed=1.0      # 正常语速
                )
                
                # 保存音频
                sf.write(output_path, audio, 24000)
                print(f"已为论文 {paper_id} 生成语音: {output_path}")
            except Exception as e:
                print(f"使用CosyVoice生成语音失败: {e}")
                self._generate_fallback_audio(script, output_path)
        else:
            # 使用备用方案
            self._generate_fallback_audio(script, output_path)
        
        return output_path
    
    def _generate_fallback_audio(self, script: str, output_path: str):
        """生成备用音频（当CosyVoice不可用时）
        
        Args:
            script: 文案内容
            output_path: 输出路径
        """
        try:
            # 尝试使用系统TTS命令
            if os.name == 'posix':  # Linux/Mac
                subprocess.run(['say', '-o', output_path, script], check=True)
            elif os.name == 'nt':  # Windows
                # 保存为临时文本文件
                temp_txt = output_path.replace('.wav', '.txt')
                with open(temp_txt, 'w', encoding='utf-8') as f:
                    f.write(script)
                
                # 使用PowerShell的TTS功能
                ps_script = f'''
                Add-Type -AssemblyName System.Speech
                $synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $synthesizer.SetOutputToWaveFile("{output_path}")
                $synthesizer.Speak([System.IO.File]::ReadAllText("{temp_txt}"))
                $synthesizer.Dispose()
                '''
                subprocess.run(['powershell', '-Command', ps_script], check=True)
                
                # 删除临时文件
                if os.path.exists(temp_txt):
                    os.remove(temp_txt)
            
            print(f"已使用系统TTS生成备用音频: {output_path}")
        except Exception as e:
            print(f"生成备用音频失败: {e}")
            # 生成一个静音音频文件
            sample_rate = 24000
            duration = 5  # 5秒
            silence = np.zeros(sample_rate * duration)
            sf.write(output_path, silence, sample_rate)
            print(f"已生成静音音频: {output_path}")

if __name__ == "__main__":
    # 测试语音生成
    generator = VoiceGenerator()
    script_path = "scripts/script_01_2304.12345.txt"
    
    # 如果测试文件不存在，创建一个
    if not os.path.exists(script_path):
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文案，用于测试语音合成功能。这篇论文介绍了一种新的人工智能方法，可以提高模型的性能。")
    
    audio_path = generator.generate_voice(script_path, "2304.12345", 0)
    print(f"生成的音频: {audio_path}") 