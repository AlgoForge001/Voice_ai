import os
import time
import torch
import psutil
import asyncio
import numpy as np
import sys
from pathlib import Path

# Fix for OpenMP error
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent))

from app.adapters.tts.indicparler import IndicParlerTTSAdapter, get_indicparler_adapter

def get_mem_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 * 1024)  # Return MB

async def diagnostic_run(text, language="hi", voice_id="1"):
    print(f"\n--- DIAGNOSTIC RUN: {language} ---")
    print(f"Text length: {len(text)} characters")
    
    # 1. Start Memory
    start_mem = get_mem_usage()
    print(f"Initial Memory Usage: {start_mem:.2f} MB")
    
    # 2. Model Loading
    print("Stage: Model Loading...")
    start_time = time.time()
    adapter = get_indicparler_adapter()
    load_time = time.time() - start_time
    after_load_mem = get_mem_usage()
    print(f"Model Load Time: {load_time:.2f}s")
    print(f"Memory after load: {after_load_mem:.2f} MB (Delta: {after_load_mem - start_mem:.2f} MB)")
    
    # 3. Request Start
    print("\n--- Starting Request Timeline ---")
    req_start = time.time()
    
    # Text Preprocessing
    stage_start = time.time()
    clean_text = adapter._clean_text(text)
    preprocess_time = time.time() - stage_start
    print(f"Text Preprocessing: {preprocess_time*1000:.2f}ms")
    
    # Chunking
    stage_start = time.time()
    chunks = adapter._chunk_text(clean_text)
    chunking_time = time.time() - stage_start
    print(f"Chunking: {chunking_time*1000:.2f}ms ({len(chunks)} chunks)")
    
    # Voice Description
    stage_start = time.time()
    description = adapter._get_voice_description(voice_id, language)
    desc_token_start = time.time()
    description_input_ids = adapter.description_tokenizer(
        description, 
        return_tensors="pt"
    ).to(adapter.device)
    voice_desc_time = time.time() - stage_start
    print(f"Voice Desc & Tokenization: {voice_desc_time*1000:.2f}ms")
    
    all_audio = []
    total_inference_time = 0
    chunk_metrics = []
    
    # Process Chunks
    for i, chunk in enumerate(chunks):
        print(f"  Processing Chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
        
        # Chunk Tokenization
        t_start = time.time()
        prompt_input_ids = adapter.tokenizer(
            chunk, 
            return_tensors="pt"
        ).to(adapter.device)
        token_time = time.time() - t_start
        
        # Chunk Inference
        inf_start = time.time()
        with torch.no_grad():
            generation = adapter.model.generate(
                input_ids=description_input_ids.input_ids,
                attention_mask=description_input_ids.attention_mask,
                prompt_input_ids=prompt_input_ids.input_ids,
                prompt_attention_mask=prompt_input_ids.attention_mask
            )
        inf_time = time.time() - inf_start
        total_inference_time += inf_time
        
        # Post-process chunk
        p_start = time.time()
        audio_arr = generation.cpu().numpy().squeeze()
        all_audio.append(audio_arr)
        post_time = time.time() - p_start
        
        chunk_metrics.append({
            "token": token_time,
            "inference": inf_time,
            "post": post_time,
            "chars": len(chunk)
        })
        
        print(f"    - Inf: {inf_time:.2f}s, Token: {token_time*1000:.2f}ms")

    # 4. Storage / Save
    stage_start = time.time()
    final_audio = np.concatenate(all_audio) if len(all_audio) > 1 else all_audio[0]
    
    import tempfile
    from scipy.io import wavfile
    import soundfile as sf
    
    temp_dir = Path(tempfile.gettempdir()) / "diag_tts"
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / f"diag_{language}_{int(time.time())}.wav"
    
    sf.write(
        str(temp_path),
        final_audio,
        adapter.model.config.sampling_rate
    )
    storage_time = time.time() - stage_start
    
    total_time = time.time() - req_start
    after_req_mem = get_mem_usage()
    
    print("\n--- FINAL TIMELINE SUMMARY ---")
    print(f"1. Preprocessing: {preprocess_time*1000:.2f}ms")
    print(f"2. Chunking:      {chunking_time*1000:.2f}ms")
    print(f"3. Voice Desc:    {voice_desc_time*1000:.2f}ms")
    print(f"4. Total Token:   {sum(m['token'] for m in chunk_metrics)*1000:.2f}ms")
    print(f"5. Total Inference: {total_inference_time:.2f}s (Average: {total_inference_time/len(chunks):.2f}s/chunk)")
    print(f"6. Post-process:   {sum(m['post'] for m in chunk_metrics)*1000:.2f}ms")
    print(f"7. Storage/Save:   {storage_time*1000:.2f}ms")
    print(f"TOTAL END-TO-END: {total_time:.2f}s")
    
    print(f"\nMemory Delta after request: {after_req_mem - after_load_mem:.2f} MB")
    print(f"Audio Duration: {len(final_audio) / adapter.model.config.sampling_rate:.2f}s")
    print(f"RTF (Real-Time Factor): {total_time / (len(final_audio) / adapter.model.config.sampling_rate):.2f}")

    return {
        "total_time": total_time,
        "inf_time": total_inference_time,
        "mem_delta": after_req_mem - after_load_mem
    }

async def main():
    # Test 1: Short Hindi Sentence
    text_short = "नमस्ते, यह एक छोटा परीक्षण है।"
    await diagnostic_run(text_short)
    
    # Test 2: Medium Hindi Paragraph (~250 chars)
    text_med = "भारत एक विविधताओं वाला देश है जहाँ कई भाषाएँ बोली जाती हैं। हिंदी यहाँ की प्रमुख भाषा है और इसे समझने वाले लोग पूरे देश में फैले हुए हैं। तकनीक के माध्यम से अब हम इन भाषाओं को डिजिटल दुनिया में और भी प्रभावी ढंग से उपयोग कर सकते हैं।"
    await diagnostic_run(text_med)

    print("\n--- System Context ---")
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print(f"CPU Count: {os.cpu_count()}")

if __name__ == "__main__":
    asyncio.run(main())
