# N60 Pro ImmortalWrt 24.10.6 Overlay Build

Overlay repository for Netcore N60 Pro custom ImmortalWrt firmware.

## 快速開始（繁體中文）

這是 **Netcore N60 Pro 開源 mt76 Wi-Fi 驅動修補版**，使用固定的
ImmortalWrt 24.10.6 原始碼，目標是驗證 2026-09-16 的 Kernel Panic 修正。

1. 開啟本倉庫的 **Actions**，選擇 **Build N60 Pro (ImmortalWrt 24.10.6 + mt76 fix)**。
2. 按 **Run workflow**。預設的 `private_settings=true` 會讀取你已建立的 `ROUTER_CONFIG`，編譯含私人設定的韌體。
3. 成功後下載 `n60-pro-private-encrypted`，先解開 GitHub 下載的外層 ZIP，再使用 7-Zip 解開內部加密的 `.7z`。
4. **7z 解壓密碼就是 `ROUTER_CONFIG` 裡的 `root_password`（路由器管理員密碼）**，不需要另外計算或執行 Python 工具。

**請記住編譯當時使用的管理員密碼。** GitHub Secret 儲存後不能查看原文；如果日後更改 `root_password`，舊韌體壓縮檔仍要使用舊密碼。

如果選擇 `private_settings=false`，則不會寫入私人密碼，下載的是可直接解壓的通用測試韌體。

目前是已完成 CI 程式與靜態檢查，**尚未執行真正的雲端完整編譯或實機驗證**。第一次刷機前請先保留原版韌體與救援方式。

## 編譯快取（加速第二次以後的 Actions）

目前 GitHub Actions 使用 `actions/cache/restore@v4` / `actions/cache/save@v4` 加速重複編譯：

- **`firmware/dl`**：快取下載好的 OpenWrt/ImmortalWrt 套件原始碼；下載成功就保存，即使後續編譯失敗也可重用。
- **`firmware/.ccache`**：快取編譯器產生的 C/C++ 物件檔，設定上限 **1500 MB**；若編譯失敗，仍嘗試保存已有的快取，加速下一次除錯。
- 快取金鑰與固定版本、裝置設定和補丁關聯；變更相關設定時會以舊快取作為備援，自動重新計算編譯結果。
- **不快取** `ROUTER_CONFIG`、`firmware/files`、`firmware/bin`、`dist`、`build_dir` 或整份韌體，以防密碼外洩及過大／過期的編譯狀態。

首次編譯需要建立快取，未必比較快；第二次開始才可能節省下載與部分編譯時間。快取是否命中及可節省多久，須看實際 Actions 執行紀錄。GitHub Actions **Cache** 與下載韌體的 **Artifact** 是兩種不同的保存機制；本專案韌體 Artifact 仍為 7 天。

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

The 7z archive password is **exactly the `root_password` field in
`ROUTER_CONFIG`**, which is also configured as the router's root login password.
There is no separate decryption secret or password-derivation utility.
If you later change the router root password in GitHub Secrets, use the
**old root password** to open older firmware archives. Choose a strong root
password, since it also protects the public CI download.

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
