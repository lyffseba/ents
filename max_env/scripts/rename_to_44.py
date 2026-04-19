from huggingface_hub import HfApi

def main():
    api = HfApi()
    username = api.whoami()["name"]
    
    old_repo_id = f"{username}/ents"
    new_repo_id = f"{username}/44"
    
    print(f"Renaming repository from {old_repo_id} to {new_repo_id}...")
    
    try:
        api.move_repo(
            from_id=old_repo_id,
            to_id=new_repo_id,
            repo_type="dataset"
        )
        print(f"\nSuccessfully renamed! Check out your updated repo here: https://huggingface.co/datasets/{new_repo_id}")
    except Exception as e:
        print(f"Error renaming repository: {e}")

if __name__ == "__main__":
    main()
