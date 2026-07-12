#!/usr/bin/env python3
"""
اسکریپت اتوماسیون ساخت اینباند VLESS با پینگ بهینه روی پنل X4G (Heimdall/3x-ui) دیپلوی‌شده روی Railway.

نحوه‌ی استفاده:
    python3 auto_config.py --base-url https://YOUR-APP.up.railway.app --username admin --password YOUR_PASSWORD

این اسکریپت:
1. با یوزر/پسورد پنل لاگین می‌کند و کوکی سشن می‌گیرد
2. یک اینباند VLESS + WS روی پورت 8080 (پورت ثابت داخلی که nginx به آن proxy می‌کند) می‌سازد
3. تنظیمات را برای کمترین لتنسی ممکن انتخاب می‌کند (sniffing فعال، بدون رمزنگاری اضافه چون TLS را خودِ Railway edge انجام می‌دهد)
4. لینک کلاینت VLESS نهایی + متن ساب را چاپ می‌کند

نکته‌ی پینگ پایین: بیشترین تاثیر روی پینگ، انتخاب Region سرور در Railway است
(Settings هنگام ساخت پروژه یا در تنظیمات Environment) — برای کاربر ایران،
معمولاً Region های Europe (مثل europe-west4) یا Southeast Asia (asia-southeast1)
پینگ به‌مراتب کمتری نسبت به US می‌دهند.
"""
import argparse
import json
import sys
import uuid

import requests


def build_inbound_payload(listen_port: int, ws_path: str, remark: str):
    client_id = str(uuid.uuid4())
    settings = {
        "clients": [
            {
                "id": client_id,
                "email": remark,
                "enable": True,
                "flow": "",
            }
        ],
        "decryption": "none",
        "fallbacks": [],
    }
    stream_settings = {
        "network": "ws",
        "security": "none",
        "wsSettings": {
            "path": ws_path,
            "headers": {},
        },
    }
    sniffing = {
        "enabled": True,
        "destOverride": ["http", "tls", "quic"],
    }

    payload = {
        "up": 0,
        "down": 0,
        "total": 0,
        "remark": remark,
        "enable": True,
        "expiryTime": 0,
        "listen": "",
        "port": listen_port,
        "protocol": "vless",
        "settings": json.dumps(settings),
        "streamSettings": json.dumps(stream_settings),
        "sniffing": json.dumps(sniffing),
    }
    return payload, client_id


def main():
    parser = argparse.ArgumentParser(description="Auto-create low-ping VLESS inbound on X4G/Heimdall panel")
    parser.add_argument("--base-url", required=True, help="e.g. https://your-app.up.railway.app")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--web-base-path", default="/managepanel/", help="matches -webBasePath from start.sh")
    parser.add_argument("--listen-port", type=int, default=8080, help="fixed internal port nginx proxies to")
    parser.add_argument("--ws-path", default="/cdn")
    parser.add_argument("--remark", default="X4G-LowPing")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    base_path = args.web_base_path if args.web_base_path.startswith("/") else "/" + args.web_base_path
    base_path = base_path.rstrip("/") + "/"

    session = requests.Session()

    login_url = f"{base}{base_path}login"
    resp = session.post(login_url, data={"username": args.username, "password": args.password}, timeout=20)
    resp.raise_for_status()
    login_json = resp.json()
    if not login_json.get("success", False):
        print(f"❌ Login failed: {login_json}", file=sys.stderr)
        sys.exit(1)
    print("✅ Login OK")

    payload, client_id = build_inbound_payload(args.listen_port, args.ws_path, args.remark)
    add_url = f"{base}{base_path}panel/inbound/add"
    resp = session.post(add_url, data=payload, timeout=20)
    resp.raise_for_status()
    add_json = resp.json()
    if not add_json.get("success", False):
        print(f"❌ Inbound creation failed: {add_json}", file=sys.stderr)
        sys.exit(1)
    print("✅ Inbound created")

    domain = base.replace("https://", "").replace("http://", "")
    vless_link = (
        f"vless://{client_id}@{domain}:443?encryption=none&security=tls"
        f"&sni={domain}&fp=chrome&type=ws&host={domain}&path={args.ws_path.replace('/', '%2F')}#{args.remark}"
    )
    print("\n🔗 لینک کلاینت VLESS:")
    print(vless_link)
    print("\n📋 UUID:", client_id)


if __name__ == "__main__":
    main()
