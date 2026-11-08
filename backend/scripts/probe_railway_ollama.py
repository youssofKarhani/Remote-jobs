"""Probe Railway Backend container to cv-extractor-llm private connectivity."""
import subprocess
import shutil
import json

def test_ollama_private_reachability():
    railway_bin = shutil.which("railway") or "railway.exe"
    # Inside the Backend container, run python to fetch tags from cv-extractor-llm.railway.internal:11434
    remote_cmd = "python3 -c \"import urllib.request as u; print(u.urlopen('http://cv-extractor-llm.railway.internal:11434/api/tags').read().decode())\""
    
    print(f"[1] Executing Railway SSH via {railway_bin} to Backend service...")
    proc = subprocess.run(
        [railway_bin, "ssh", "--service", "Backend", remote_cmd],
        capture_output=True,
        text=True,
        shell=True,
    )
    
    print("Return code:", proc.returncode)
    print("STDOUT:\n", proc.stdout)
    if proc.stderr:
        print("STDERR:\n", proc.stderr)
        
    if proc.returncode == 0 and "models" in proc.stdout:
        print("\n>>> SUCCESS: Ollama is reachable from Backend via private networking!")
    else:
        print("\n>>> FAILED or unexpected output.")

if __name__ == "__main__":
    test_ollama_private_reachability()
