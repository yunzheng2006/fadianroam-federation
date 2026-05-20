# FadianRoam Federation

SOPS-managed FreeRADIUS federation proxy configuration for FadianRoam.

## Architecture

```
members.enc.yaml (SOPS encrypted, in git)
        │
        ▼  GitHub Actions on push
  sops decrypt → generate-configs.py → SSH deploy
        │
        ▼
  Federation VMs (FreeRADIUS reload)
```

## Adding a new member

```bash
sops edit members.enc.yaml
# Add new member entry, save
git commit -m "update" && git push
# CI/CD auto-deploys to all federation proxies
```

## Member entry format

```yaml
- realm: example.fadianroam.net
  name: Example Site
  mgmt_ip: 172.172.10.XX
  shared_secret: <random-hex>
  wg_pubkey: <wireguard-public-key>
```

## Setup

Requires `sops` and `age` installed locally for editing encrypted files.

```bash
brew install sops age   # macOS
apt install age         # Debian, then install sops binary
```
