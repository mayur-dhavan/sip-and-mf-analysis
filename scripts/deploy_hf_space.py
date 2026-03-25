"""Deploy the ML model and Gradio app to a Hugging Face Space."""

from huggingface_hub import HfApi, create_repo
from pathlib import Path
import shutil
import sys

SPACE_ID = "mayur6901/sip-mf-volatility-predictor"
MODEL_PATH = Path("backend/models/volatility_model.pkl")
SPACE_DIR = Path("huggingface_space")


def main():
    api = HfApi()

    # Verify authentication
    user = api.whoami()
    print(f"Authenticated as: {user['name']}")

    # 1. Create the Space repo (no-op if it already exists)
    print(f"\nCreating Space: {SPACE_ID} ...")
    url = create_repo(
        repo_id=SPACE_ID,
        repo_type="space",
        space_sdk="gradio",
        exist_ok=True,
        private=False,
    )
    print(f"Space URL: {url}")

    # 2. Upload Gradio app files
    print("\nUploading app files ...")
    api.upload_folder(
        repo_id=SPACE_ID,
        repo_type="space",
        folder_path=str(SPACE_DIR),
        commit_message="Deploy Gradio app for MF volatility prediction",
    )

    # 3. Upload the model artifact
    if not MODEL_PATH.exists():
        print(f"\nERROR: Model file not found at {MODEL_PATH}")
        print("Train the model first with: python scripts/train_model.py")
        sys.exit(1)

    size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)
    print(f"\nUploading model ({size_mb:.1f} MB) ...")
    api.upload_file(
        path_or_fileobj=str(MODEL_PATH),
        path_in_repo="volatility_model.pkl",
        repo_id=SPACE_ID,
        repo_type="space",
        commit_message="Upload trained volatility model",
    )

    print(f"\n✅ Space deployed successfully!")
    print(f"   URL: https://huggingface.co/spaces/{SPACE_ID}")
    print(f"   API: https://mayur6901-sip-mf-volatility-predictor.hf.space/")


if __name__ == "__main__":
    main()
