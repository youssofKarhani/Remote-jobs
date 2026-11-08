"""Inspect production database candidate records via Railway SSH to ensure zero mutation."""
import subprocess
import shutil

def check_prod_db():
    railway_bin = shutil.which("railway") or "railway.exe"
    # Query production database users
    remote_cmd = (
        "python3 -c \""
        "from app.database import SessionLocal; "
        "from app.models.user import User; "
        "db = SessionLocal(); "
        "users = db.query(User).all(); "
        "print('PROD_USER_COUNT:', len(users)); "
        "print('PROD_EMAILS:', [u.email for u in users]); "
        "db.close()\""
    )
    proc = subprocess.run(
        [railway_bin, "ssh", "--service", "Backend", remote_cmd],
        capture_output=True,
        text=True,
        shell=True,
    )
    print("STDOUT:\n", proc.stdout)
    if proc.stderr:
        print("STDERR:\n", proc.stderr)

if __name__ == "__main__":
    check_prod_db()
