from huggingface_hub import HfApi
import os

def main():
    api = HfApi()
    
    # 1. Get your username automatically
    username = api.whoami()["name"]
    repo_name = "44"
    repo_id = f"{username}/{repo_name}"
    
    print(f"Creating repository: {repo_id}")
    
    # 2. Create the repository
    api.create_repo(
        repo_id=repo_id,
        repo_type="dataset", # Using dataset type since it's code/learning materials
        private=False,
        exist_ok=True
    )
    print("Repository created successfully!")
    
    # 3. Upload the current workspace (excluding max_env environments)
    print("Uploading project files...")
    
    # We will upload the README and src files specifically to keep it clean
    api.upload_file(
        path_or_fileobj="../README.md",
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset"
    )
    
    api.upload_folder(
        folder_path="src",
        path_in_repo="src",
        repo_id=repo_id,
        repo_type="dataset"
    )
    
    print(f"\nUpload complete! Check out your repo here: https://huggingface.co/datasets/{repo_id}")

if __name__ == "__main__":
    main()
