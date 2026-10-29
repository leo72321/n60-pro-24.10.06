# N60 Pro ImmortalWrt 24.10.6 Overlay Build

Overlay repository for Netcore N60 Pro custom ImmortalWrt firmware.

## 快速開始（繁體中文）

這是 **Netcore N60 Pro 開源 mt76 Wi-Fi 驅動修補版**，使用固定的
ImmortalWrt 24.10.6 原始碼，目標是驗證 2026-09-16 的 Kernel Panic 修正。

1. 開啟本倉庫的 **Actions**，選擇 **Build N60 Pro (ImmortalWrt 24.10.6 + mt76 fix)**。
2. 按 **Run workflow**。預設的 `private_settings=true` 會讀取你已建立的 `ROUTER_CONFIG`，編譯含私人設定的韌體。
3. 成功後下載 `n60-pro-private-encrypted`，先解開 GitHub 下載的外層 ZIP，再使用 7-Zip 解開內部加密的 `.7z`。
4. 解密密碼由完整的六項 `ROUTER_CONFIG` 值產生。Windows 可執行 `scripts/get_archive_password.pyw`（需要安裝 Python），選取自己保存的設定 JSON 後複製密碼。

**請務必保存自己的 ROUTER_CONFIG JSON 副本。** GitHub Secret 儲存後不能再次顯示原文；改了設定，舊韌體壓縮檔仍須使用原本六項設定才能解密。

如果選擇 `private_settings=false`，則不會寫入私人密碼，下載的是可直接解壓的通用測試韌體。

目前是已完成 CI 程式與靜態檢查，**尚未執行真正的雲端完整編譯或實機驗證**。第一次刷機前請先保留原版韌體與救援方式。

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

## Wi-Fi kernel panic fix (2026-09-16 backport)

The GitHub Actions workflow builds a **minimal N60 Pro sysupgrade firmware**
using pinned ImmortalWrt 24.10.6 source and its existing open-source
`mt76` / `mt7915e` drivers. It adds
`patches/mt76/999-fix-8023-offload-tx-info-band.patch` to
`package/kernel/mt76/patches/`, so the driver is fixed during compilation.

- ImmortalWrt commit: `5fa11a1b5689154d296fdacf1e16a7abccb897b9`
- mt76 source: `eb567bc7f9b692bbf1ddfe31dd740861c58ec85b`
- Device: `mediatek/filogic`, `netcore_n60-pro`
- Selected UI: LuCI with Traditional Chinese language package
- Existing custom packages are copied into the build tree, but **not selected**
  for this first minimal Wi-Fi validation build.
- The historical `diffs/` changes are deliberately not applied until the
  base crash-fix image builds successfully.

**Verification status:** The revision and patch content have been inspected.
The full firmware build has not yet been run or verified on a physical router.
A successful compilation also does not prove the original Wi-Fi crash is fixed.

## Build firmware on GitHub Actions

1. Open **Actions** in this repository and select
   **Build N60 Pro (ImmortalWrt 24.10.6 + mt76 fix)**.
2. Click **Run workflow**. The `private_settings` input is enabled by default.
3. For a private image, add **one repository Secret** named `ROUTER_CONFIG`
   under Settings > Secrets and variables > Actions.

Example JSON (replace with your actual private values in the GitHub Secret,
**not in tracked source files**):

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

The six values must be strings. Both PPPoE values can be empty only when PPPoE
is not used.

### Download the result

**Private mode** (`private_settings=true`, default):
The runner generates `files/etc/uci-defaults/99-router-config` from the
Secret and embeds it in the image. Since firmware images expose embedded
`/rom/etc/uci-defaults` scripts, the workflow wraps the firmware and SHA256
checksums in a password-protected **AES-256 7z archive** before uploading the
Actions artifact called `n60-pro-private-encrypted`.

The password is derived deterministically from the entire ROUTER_CONFIG JSON,
so **keep a private copy of those six values**. On Windows with Python installed,
run `scripts/get_archive_password.pyw`, select your saved JSON file, and
paste the copied password into 7-Zip. The script processes the JSON locally.
If you change the Secret after building, old archives require the original
values.

**Generic mode** (`private_settings=false`): Builds with no private
`uci-defaults` settings and uploads an unencrypted
`n60-pro-generic-sysupgrade` artifact.

**Security:** Do not upload an unencrypted private firmware or raw router
configuration to a public GitHub Release, Actions artifact, issue, or commit.
7z archive security still depends on the strength of your configuration
passwords. GitHub Actions artifacts expire after seven days.

### Flash safety

Only use the generated **N60 Pro sysupgrade.itb** for a compatible device
already running the appropriate OpenWrt/ImmortalWrt sysupgrade scheme.
Keep a working backup and recovery path; do not flash bootloader/preloader
images as part of this test. First-boot settings can change the LAN IP
and Wi-Fi credentials and disconnect your current session.

The GitHub-hosted runner has limited disk space. The workflow removes unused
toolchains and performs a minimal build, but a real Actions run is required to
verify dependency availability, disk usage, and final image generation.
