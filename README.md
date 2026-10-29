# N60 Pro ImmortalWrt 24.10.6 Overlay Build

Overlay repository for Netcore N60 Pro custom ImmortalWrt firmware.

## Upstream

- **Repository**: immortalwrt/immortalwrt
- **Tag**: v24.10.6
- **Commit**: 5fa11a1b5689154d296fdacf1e16a7abccb897b9
- **mt76 PKG_SOURCE_VERSION**: eb567bc7f9b692bbf1ddfe31dd740861c58ec85b
- **Linux Kernel**: 6.6.x (mediatek/filogic)

## Directory Structure

```
.github/workflows/   GitHub Actions build workflow
patches/mt76/        mt76 backport patches
packages/            Custom packages (bandix, netspeedtest, etc.)
files/               uci-defaults and other overlay files
diffs/               Diffs applied to immortalwrt source tree
```

## Custom Packages

- `bandix` + `luci-app-bandix` — Network traffic monitor
- `bandix-plus` + `luci-app-bandix-plus` — Network traffic monitor (plus)
- `luci-app-netspeedtest` — Speed test (iperf3 + librespeed)

## Patches

- `patches/mt76/999-fix-8023-offload-tx-info-band.patch` — Backport: wifi: mt76: initialize tx_info band for 802.3 offload (2026-09-16)

## Source Modifications (diffs/)

- `include-host-build.mk.diff` — FORCE_UNSAFE_CONFIGURE=1
- `config_generate.diff` — Default timezone: Asia/Taipei / CST-8
- `99-default-settings.diff` — Default language: zh_cn
- `99-default-settings-chinese.diff` — Timezone: Asia/Taipei

## ROUTER_CONFIG: private router settings

Configure one repository secret named `ROUTER_CONFIG` in
Settings > Secrets and variables > Actions > New repository secret.

The secret holds a single JSON object. Replace these **example** values with yours:

```json
{
  "wlan_name": "MyWiFi",
  "wlan_password": "example-only-password",
  "root_password": "example-only-root-password",
  "lan_ip_address": "192.168.100.1",
  "pppoe_username": "",
  "pppoe_password": ""
}
```

All six fields must be strings; use empty PPPoE fields together if PPPoE is unused.
GitHub does not show secret values after they have been saved. Keep your own secure copy.

The manual GitHub Actions workflow validates this secret and creates
`files/etc/uci-defaults/99-router-config` only inside its temporary runner workspace.
The generated file is ignored by Git, never committed, and not uploaded by this workflow.
The template is stored in `templates/uci-defaults/`, and the Python generator in `scripts/`.

**Build status:** The workflow currently prepares private first-boot settings, but firmware compilation has not yet been implemented in this overlay repository.

**Security warning:** Credentials embedded in the finished firmware are extractable from
`/rom/etc/uci-defaults/`. Do not publicly upload or release a firmware image containing private credentials, even if the source repository is public.
