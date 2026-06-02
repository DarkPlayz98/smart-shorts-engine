import os
import sys
import time
import base64
import requests
import subprocess
import json
import urllib.parse

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")

def check_keys():
    if not GEMINI_KEY or not ELEVEN_KEY:
        print("[-] Critical Error: Missing API Keys.")
        sys.exit(1)

def generate_master_blueprint():
    print("[+] 1. Gemini Flash Extended Engine crafting script and 10 cinematic image prompts...")
    host = "https://" + "generativelanguage.googleapis.com"
    url = f"{host}/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    prompt = (
        "Write a mesmerizing 60-second voiceover script about financial leverage and the 10X mindset. "
        "Next, provide exactly 10 highly detailed IMAGE generation prompts specifying a photorealistic, dark luxury aesthetic with neon reflections and vertical 9:16 framing. "
        "Format the output exactly as a single JSON object: "
        '{"script": "voiceover text here", "image_prompts": ["prompt 1", "prompt 2", "...", "prompt 10"]}'
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:-3].strip()
        
    data = json.loads(raw_text)
    return data["script"], data["image_prompts"]

def generate_premium_voice(text):
    print("[+] 2. ElevenLabs synthesizing narrative...")
    host = "https://" + "api.elevenlabs.io"
    url = f"{host}/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb"
    
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.85}
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    with open("long_voice.mp3", "wb") as f:
        f.write(response.content)
    print("[+++] Master audio track saved.")

def generate_and_animate_images(prompts):
    print("[+] 3. Pollinations.ai generating and animating 10 scenes (Bypassing Rate Limits)...")
    
    with open("clip_list.txt", "w") as f_list:
        for i, prompt in enumerate(prompts):
            print(f"[*] Generating scene {i+1}/10...")
            
            # Encodes the Gemini prompt securely for a URL request
            encoded_prompt = urllib.parse.quote(prompt)
            img_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){encoded_prompt}?width=1080&height=1920&nologo=true"

            img_filename = f"scene_{i}.jpg"
            clip_filename = f"clip_{i}.mp4"

            try:
                # Direct grab, no API keys, no rate limits
                res = requests.get(img_url, timeout=30)
                res.raise_for_status()

                with open(img_filename, "wb") as f_img:
                    f_img.write(res.content)

                print(f"[*] Applying cinematic zoom to scene {i+1}...")
                zoom_cmd = (
                    f'ffmpeg -y -loop 1 -i {img_filename} -t 5 '
                    f'-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,'
                    f'zoompan=z=\'min(zoom+0.0015,1.5)\':d=125:x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':s=1080x1920" '
                    f'-c:v libx264 -pix_fmt yuv420p {clip_filename} -loglevel error'
                )
                subprocess.run(zoom_cmd, shell=True, check=True)
                f_list.write(f"file '{clip_filename}'\n")

            except Exception as e:
                print(f"[-] Scene {i+1} failed: {e}")

def compile_masterwork():
    print("[+] 4. FFmpeg concatenating timeline and layering audio...")

    with open("clip_list.txt", "r") as f:
        clips = [l for l in f.readlines() if l.strip()]
    if not clips:
        print("[-] No clips were generated. Aborting compilation.")
        return

    output_path = "dark_profito_master.mp4"
    subprocess.run(
        "ffmpeg -y -f concat -safe 0 -i clip_list.txt -c copy continuous_bg.mp4 -loglevel error",
        shell=True, check=True
    )
    subprocess.run(
        f"ffmpeg -y -i continuous_bg.mp4 -i long_voice.mp3 -map 0:v -map 1:a "
        f"-c:v copy -c:a aac -shortest {output_path} -loglevel error",
        shell=True, check=True
    )
    print(f"[+++] SUCCESS: Saved to {output_path}")

if __name__ == "__main__":
    print("=== INITIALIZING CINEMATIC AUTOMATION ENGINE ===")
    try:
        check_keys()
        script, prompts = generate_master_blueprint()
        generate_premium_voice(script)
        generate_and_animate_images(prompts)
        compile_masterwork()
        print("=== COMPILATION COMPLETE ===")
    except Exception as e:
        print(f"[-] Pipeline Failed: {e}")
