from std.pathlib import Path


def encode_fangorn(text: String) -> String:
    # Tiny Shakespeare is ASCII: unique bytes == unique characters.
    var bytes = text.as_bytes()
    var seen = List[Int]()
    for i in range(len(bytes)):
        var b = Int(bytes[i])
        var found = False
        for si in range(len(seen)):
            if seen[si] == b:
                found = True
                break
        if not found:
            seen.append(b)

    for a in range(len(seen)):
        var j = a
        while j > 0 and seen[j] < seen[j - 1]:
            var tmp = seen[j]
            seen[j] = seen[j - 1]
            seen[j - 1] = tmp
            j -= 1

    var sample = String("Fangorn")
    var sb = sample.as_bytes()
    var out = String("[")
    for si in range(len(sb)):
        var target = Int(sb[si])
        var id = 0
        for k in range(len(seen)):
            if seen[k] == target:
                id = k
                break
        if si > 0:
            out += ", "
        out += String(id)
    out += "]"
    return out


def main() raises:
    var path = Path("input.txt")
    if not path.exists():
        print("Please place Tiny Shakespeare in input.txt")
        return
    var text = path.read_text()
    print("Final Array for the Ent's brain to read:", encode_fangorn(text))
