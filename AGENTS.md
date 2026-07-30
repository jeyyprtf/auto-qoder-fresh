# Qoder Autopilot (local)

Upstream: [Daivageralda/qoder-autopilot](https://github.com/Daivageralda/qoder-autopilot) v0.6.3

## Local wire-up
- Temp mail: **same CF worker as Grok** → `https://mail-api.jujukaizen.web.id` (domain `jujukaizen.web.id`)
- API shape: dreamhunter `cloudflare_temp_email` (`/api/new_address` + JWT + `/api/mails`) — patched in `infra/temp_mail.py`
- 9router DB: `~/.9router/db/data.sqlite`
- Config: `.env` (gitignored) or `~/.qoder-autopilot/config.json`

## Run
```bash
source .venv/bin/activate
qoder-autopilot doctor
# first real run (manual captcha, show browser)
qoder-autopilot --manual-captcha --no-headless -n 1
# skip 9router inject
qoder-autopilot --manual-captcha --no-oauth
```

## Notes
- Pro trial = 1 account/user; extra trials get frozen (Qoder ToS)
- Captcha: Aliyun slider — manual mode most reliable on VPS without AI key
- VPS: need display or xvfb + non-headless for manual captcha

## Claim trial (no desktop / no browser for claim itself)
Friend flow: spoof machine → CLI login → mint PAT (Integrations).

```bash
# install CLI once
npm i -g @qoder-ai/qodercli

qoder-autopilot vm-check          # warn if obvious VM
qoder-autopilot spoof             # reset machineid + telemetry + clean fingerprint files
qoder-autopilot claim             # spoof + qodercli login (prints URL on headless)
# after login: qoder.com → Account → Integrations → create PAT
# buyer: export QODER_PERSONAL_ACCESS_TOKEN=<pat>
```

- **Desktop app not required** for claim — only `qodercli`
- Browser only needed for *new account signup* (or completing device URL on phone)
- Isolated multi-account: `qoder-autopilot claim --cli-dir /tmp/qoder-acc1`
