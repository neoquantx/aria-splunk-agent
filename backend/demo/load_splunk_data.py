import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import splunklib.client as splunk_client
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SPLUNK_HOST = os.getenv("SPLUNK_HOST", "localhost")
SPLUNK_PORT = int(os.getenv("SPLUNK_PORT", "8089"))
SPLUNK_USER = os.getenv("SPLUNK_USERNAME", "admin")
SPLUNK_PASS = os.getenv("SPLUNK_PASSWORD", "")

BASE_TIME = datetime(2026, 5, 20, 1, 15, 0)

def ts(minutes_offset=0):
    t = BASE_TIME + timedelta(minutes=minutes_offset)
    return t.strftime("%Y-%m-%dT%H:%M:%S")

def main():
    print("Connecting to Splunk...")
    try:
        service = splunk_client.connect(
            host=SPLUNK_HOST,
            port=SPLUNK_PORT,
            username=SPLUNK_USER,
            password=SPLUNK_PASS,
        )
        print("Connected successfully")
    except Exception as e:
        print(f"FAILED to connect: {e}")
        print("Check SPLUNK_PASS is correct in this script")
        sys.exit(1)

    idx = service.indexes["main"]
    ok = 0
    fail = 0

    def send(text, sourcetype):
        nonlocal ok, fail
        try:
            idx.submit(text, sourcetype=sourcetype, host="web-server-01")
            ok += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            fail += 1

    print("Loading brute force SSH events (20)...")
    for i in range(20):
        send(
            f'{ts(i)} web-server-01 sshd[1234]: Failed password for admin from 185.220.101.47 port {22000+i} ssh2 action=failure src_ip=185.220.101.47 user=admin',
            "linux_secure"
        )

    print("Loading successful login (1)...")
    send(
        f'{ts(20)} web-server-01 sshd[1234]: Accepted password for admin from 185.220.101.47 port 22847 ssh2 action=success src_ip=185.220.101.47 user=admin',
        "linux_secure"
    )

    print("Loading command execution events (6)...")
    for i, cmd in enumerate(["whoami", "id", "uname -a", "cat /etc/passwd", "ps aux", "netstat -an"]):
        send(
            f'{ts(21+i)} web-server-01 sshd[1235]: Command executed NewProcessName={cmd} EventCode=4688 user=admin src_ip=185.220.101.47 action=success',
            "linux_secure"
        )

    print("Loading lateral movement events (3)...")
    for src, dest, user, offset in [
        ("web-server-01", "internal-host-02", "svc-web", 37),
        ("web-server-01", "internal-host-03", "svc-web", 55),
        ("internal-host-02", "internal-host-03", "svc-admin", 75),
    ]:
        send(
            f'{ts(offset)} {src} sshd[1236]: Accepted password for {user} from {src} to {dest} action=success src_ip={src} dest={dest} user={user}',
            "linux_secure"
        )

    print("Loading C2 outbound traffic events (5)...")
    for i in range(5):
        send(
            f'{ts(76+i)} internal-host-03 kernel: OUTBOUND src=internal-host-03 dest_ip=45.142.212.100 dest_port=443 bytes={1024*(i+1)} protocol=HTTPS action=allowed',
            "stream:tcp"
        )

    print("Loading data exfiltration event (1)...")
    send(
        f'{ts(92)} internal-host-03 kernel: LARGE_TRANSFER src=internal-host-03 dest_ip=45.142.212.100 dest_port=443 bytes=157286400 bytes_out=157286400 action=allowed',
        "stream:tcp"
    )

    print("Loading anomaly detection events (3)...")
    send(f'{ts(95)} web-server-01 aria_ml: anomaly_score=0.94 src_ip=185.220.101.47 reason=unusual_login_pattern user=admin', "aria_anomaly")
    send(f'{ts(96)} internal-host-03 aria_ml: anomaly_score=0.89 src_ip=45.142.212.100 reason=data_volume_spike bytes=157286400', "aria_anomaly")
    send(f'{ts(97)} internal-host-02 aria_ml: anomaly_score=0.76 src_ip=internal-host-03 reason=new_outbound_connection', "aria_anomaly")

    print(f"\nFINAL: {ok} sent, {fail} failed out of {ok+fail} total")
    if fail == 0:
        print("All data loaded — ARIA agents can now query real Splunk data!")
    else:
        print("Some events failed — check Splunk connection and password")

if __name__ == "__main__":
    main()
