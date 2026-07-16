from std.python import Python

fn main() raises:
    # We are using Mojo's superpower: directly talking to Python!
    # Let's import the standard Python libraries.
    var os = Python.import_module("os")
    var urllib = Python.import_module("urllib.request")
    
    var file_path = "input.txt"
    var dataset_url = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
    
    print("Checking if we have the book for the Ents...")
    
    # Check if the file already exists
    if not os.path.exists(file_path):
        print("Downloading Tiny Shakespeare (1MB)...")
        _ = urllib.urlretrieve(dataset_url, file_path)
        print("Download complete!")
    else:
        print("We already have the book!")
        
    # Read how many characters are in it
    var builtins = Python.import_module("builtins")
    var f = builtins.open(file_path, "r")
    var text = f.read()
    f.close()
    
    print("The Ent's book has", len(text), "characters to read.")
