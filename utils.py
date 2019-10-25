import subprocess

def run_cmd(cmd: str, directory: str):
    pr = subprocess.Popen(cmd , cwd=directory, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = pr.communicate()
    return out, error


