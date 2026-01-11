import os, shutil, subprocess, secrets
from pathlib import Path

CKPT_PATH = Path("/tmp/checkpoint-2814")
MODEL_DIR = Path("./model")
MODEL_DIR.mkdir(exist_ok=True)

required_files = [
    "adapter_model.safetensors","adapter_config.json","tokenizer.json",
    "tokenizer_config.json","special_tokens_map.json","added_tokens.json",
    "merges.txt","vocab.json","chat_template.jinja"
]

for f in required_files:
    src = CKPT_PATH / f
    dst = MODEL_DIR / f
    if src.exists():
        shutil.copy(src, dst)
        print(f"✓ Copied {f}")
    else:
        print(f"⚠️ Missing {f}")

DOCKER_USER = os.environ['DOCKER_USERNAME']
DOCKER_PASS = os.environ['DOCKER_PAT']
IMAGE_NAME = "vk-llm"
IMAGE_TAG = "latest"
image_full_name = f"{DOCKER_USER}/{IMAGE_NAME}:{IMAGE_TAG}"
api_key = secrets.token_hex(16)
print(f"Generated API key: {api_key}")

subprocess.run(["docker","login","-u",DOCKER_USER,"-p",DOCKER_PASS],check=True)
subprocess.run(["docker","build","-t",image_full_name,"."],check=True)
subprocess.run(["docker","push",image_full_name],check=True)
print(f"✅ Docker image pushed: {image_full_name}")

RENDER_API_KEY = os.environ['RENDER_API_KEY']
RENDER_SERVICE_NAME = "vk-llm-api"
subprocess.run(["render","login","--api-key",RENDER_API_KEY],check=True)
try:
    subprocess.run(["render","services","create","web",
                    "--name",RENDER_SERVICE_NAME,
                    "--image",image_full_name,
                    "--plan","free",
                    "--region","oregon"],check=True)
except subprocess.CalledProcessError:
    subprocess.run(["render","services","update","web",
                    "--name",RENDER_SERVICE_NAME,
                    "--image",image_full_name],check=True)
subprocess.run(["render","services","env-var","set",
                "--service",RENDER_SERVICE_NAME,
                "--name","API_KEY",
                "--value",api_key],check=True)
print("🚀 Render service deployed and API_KEY set!")
