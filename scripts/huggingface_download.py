# pip install huggingface_hub
import time
from huggingface_hub import snapshot_download
from huggingface_hub.utils import HfHubHTTPError

def download_with_retry(repo_id, local_dir, retries=5, delay=10):
    for i in range(retries):
        try:
            print(f"Downloading {repo_id} to {local_dir} (Attempt {i+1}/{retries})...")
            snapshot_download(repo_id, local_dir=local_dir, resume_download=True, local_dir_use_symlinks=False)
            print(f"Successfully downloaded {repo_id}")
            return True
        except (HfHubHTTPError, Exception) as e:
            print(f"Error downloading {repo_id}: {e}")
            if i < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to download {repo_id} after {retries} attempts.")
                return False

# https://huggingface.co/coqui/XTTS-v2
download_with_retry('coqui/XTTS-v2', local_dir='models/TTS/XTTS-v2')

# https://huggingface.co/Qwen/Qwen1.5-4B-Chat
download_with_retry('Qwen/Qwen1.5-4B-Chat', local_dir='models/LLM/Qwen1.5-4B-Chat')

# https://huggingface.co/Qwen/Qwen1.5-1.8B-Chat
download_with_retry('Qwen/Qwen1.5-1.8B-Chat', local_dir='models/LLM/Qwen1.5-1.8B-Chat')

# https://huggingface.co/Systran/faster-whisper-large-v3
download_with_retry('Systran/faster-whisper-large-v3', local_dir='models/ASR/whisper/faster-whisper-large-v3')
