from std.python import Python

fn main() raises:
    print("--- The Ent's Lexicon ---")
    print("A computer cannot read the letter 'A'. It only understands numbers.")
    print("A Tokenizer is a secret decoder ring that assigns a unique number to every letter.")
    
    var builtins = Python.import_module("builtins")
    var os = Python.import_module("os")
    
    var file_path = "atomic_gpt/input.txt"
    if not os.path.exists(file_path):
        print("Please run prepare_data.mojo first!")
        return
        
    var f = builtins.open(file_path, "r")
    var text: String = String(f.read())
    f.close()
    
    # Run the tokenizer logic completely inside python to simplify the Mojo script for beginners
    var py_code = """
chars = sorted(list(set(text)))
vocab_size = len(chars)

print(f"\\nVocabulary Size: {vocab_size}")
print("These are all the unique characters the Ent will ever know:")
print("".join(chars))

print("\\nExample of the Decoder Ring:")
stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }

sample_word = 'Fangorn'
print(f"Translating the word '{sample_word}' into math:")
encoded_list = []
for c in sample_word:
    # Use 0 if the character is not found
    id = stoi.get(c, 0)
    encoded_list.append(id)
    print(f"Letter '{c}' -> ID: {id}")

print(f"\\nFinal Array for the Ent's brain to read: {encoded_list}")
"""
    var locals = Python.dict()
    locals["text"] = text
    # In newer mojo we use Python.exec for evaluating statements instead of Python.evaluate 
    # But evaluating via builtins.exec is even safer
    _ = builtins.exec(py_code, locals)

