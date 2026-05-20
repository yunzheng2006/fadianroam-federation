#!/usr/bin/env python3
"""Generate FreeRADIUS and WireGuard configs from decrypted members YAML."""

import yaml
import sys
import os

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "members.dec.yaml"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "out"
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file) as f:
        data = yaml.safe_load(f)

    members = data["members"]
    federation = data["federation"]

    # --- clients.conf ---
    clients_lines = [
        'client localhost {',
        '    ipaddr = 127.0.0.1',
        '    secret = testing123',
        '    shortname = localhost',
        '}',
        '',
    ]
    for m in members:
        slug = m["realm"].replace(".", "-")
        clients_lines += [
            f'client member_{slug} {{',
            f'    ipaddr = {m["mgmt_ip"]}',
            f'    secret = {m["shared_secret"]}',
            f'    shortname = {slug}',
            '}',
            '',
        ]
    with open(os.path.join(output_dir, "clients.conf"), "w") as f:
        f.write("\n".join(clients_lines))

    # --- proxy.conf ---
    proxy_lines = [
        'proxy server {',
        '    default_fallback = no',
        '}',
        '',
    ]
    for m in members:
        slug = m["realm"].replace(".", "-")
        proxy_lines += [
            f'home_server hs_{slug} {{',
            '    type = auth+acct',
            f'    ipaddr = {m["mgmt_ip"]}',
            '    port = 1812',
            f'    secret = {m["shared_secret"]}',
            '    response_window = 20',
            '    status_check = status-server',
            '    check_interval = 30',
            '    check_timeout = 4',
            '    num_answers_to_alive = 3',
            '}',
            '',
            f'home_server_pool pool_{slug} {{',
            '    type = fail-over',
            f'    home_server = hs_{slug}',
            '}',
            '',
            f'realm {m["realm"]} {{',
            f'    pool = pool_{slug}',
            '    nostrip',
            '}',
            '',
        ]

    proxy_lines += [
        'realm LOCAL {',
        '}',
        '',
        'realm NULL {',
        '    reject = yes',
        '}',
        '',
        'realm DEFAULT {',
        '    reject = yes',
        '}',
    ]
    with open(os.path.join(output_dir, "proxy.conf"), "w") as f:
        f.write("\n".join(proxy_lines))

    # --- wireguard conf ---
    wg_lines = [
        '[Interface]',
        f'ListenPort = {federation["wg_listen_port"]}',
        f'Address = {federation["wg_interface_ip"]}/24',
        '',
    ]
    for m in members:
        wg_lines += [
            f'# Member: {m["realm"]} ({m["name"]})',
            '[Peer]',
            f'PublicKey = {m["wg_pubkey"]}',
            f'AllowedIPs = {m["mgmt_ip"]}/32',
            '',
        ]
    with open(os.path.join(output_dir, "fadianroam-mgmt.conf"), "w") as f:
        f.write("\n".join(wg_lines))

    print(f"Generated configs for {len(members)} member(s) in {output_dir}/")

if __name__ == "__main__":
    main()
