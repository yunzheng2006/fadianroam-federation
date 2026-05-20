# FadianRoam Federation

SOPS-managed FreeRADIUS federation proxy configuration for [FadianRoam](https://fadianroam.yunzheng.space).

## Architecture

```
members.enc.yaml (SOPS encrypted, secrets hidden, structure visible)
        │
        ▼  GitHub Actions on push
  sops decrypt → generate-configs.py → SSH deploy
        │
        ├──► APAC Federation Proxy (federation.yunzheng.space)
        └──► NA Federation Proxy (coming soon)
```

All federation proxies receive **identical** FreeRADIUS configs. Each Site should configure **at least two** federation proxies for redundancy.

## Joining the Federation

1. **Open an Issue** using the "Join FadianRoam Federation" template
2. Provide your realm, site name, and WireGuard public key
3. The Governance Committee reviews and approves
4. An admin adds your Site to `members.enc.yaml` and assigns your MGMT VPN IP
5. You will receive your shared secret and VPN configuration securely
6. CI/CD auto-deploys the updated config to all federation proxies

**Note:** Only admins with SOPS AGE keys can edit `members.enc.yaml`. New members cannot submit PRs to modify the encrypted config directly — use the Issue template instead.

## For Admins

### Adding a member (after approval)

```bash
sops edit members.enc.yaml
# Add new member entry with:
#   - realm, name, mgmt_ip (next available in 172.172.10.0/24)
#   - shared_secret (generate: openssl rand -hex 24)
#   - wg_pubkey (from the applicant's Issue)
git commit -m "update" && git push
# CI/CD auto-deploys to all federation proxies
```

### Adding a new federation proxy

1. Deploy FreeRADIUS + WireGuard + SOPS + AGE on the new VM
2. Generate AGE key: `age-keygen -o /etc/sops/age-key.txt`
3. Add its AGE public key to `.sops.yaml`
4. Run `sops rotate -i members.enc.yaml` to re-encrypt for the new recipient
5. Create `deploy` user with SSH key, add SSH key to GitHub Secrets
6. Add the host to `matrix.host` in `.github/workflows/deploy.yml`

### Member entry format

```yaml
- realm: example.fadianroam.net
  name: Example Site
  mgmt_ip: 172.172.10.XX
  shared_secret: <random-hex-48-chars>
  wg_pubkey: <wireguard-public-key>
```

## Setup (local)

```bash
brew install sops age   # macOS
apt install age         # Debian, then install sops binary from GitHub releases
```
