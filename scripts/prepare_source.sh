#!/usr/bin/env bash
set -euo pipefail

source_dir="${1:-firmware}"
upstream_commit='5fa11a1b5689154d296fdacf1e16a7abccb897b9'
mt76_commit='eb567bc7f9b692bbf1ddfe31dd740861c58ec85b'
patch_file='patches/mt76/999-fix-8023-offload-tx-info-band.patch'

actual_commit="$(git -C "$source_dir" rev-parse HEAD)"
if [[ "$actual_commit" != "$upstream_commit" ]]; then
  echo 'Upstream revision mismatch; refusing to patch a different tree.' >&2
  exit 1
fi
if ! grep -Fxq "PKG_SOURCE_VERSION:=$mt76_commit" "$source_dir/package/kernel/mt76/Makefile"; then
  echo 'Unexpected mt76 revision; refusing to apply this backport.' >&2
  exit 1
fi
if ! grep -Fq 'define Device/netcore_n60-pro' "$source_dir/target/linux/mediatek/image/filogic.mk"; then
  echo 'N60 Pro device definition is missing.' >&2
  exit 1
fi

# Check the patch against the exact mt76 source revision before compiling.
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
curl --fail --location --silent --show-error --retry 3 \
  "https://raw.githubusercontent.com/openwrt/mt76/$mt76_commit/tx.c" \
  --output "$tmpdir/tx.c"
patch --dry-run --batch --forward --strip=1 --directory="$tmpdir" < "$patch_file"

mkdir -p "$source_dir/package/kernel/mt76/patches" "$source_dir/package/custom"
cp "$patch_file" "$source_dir/package/kernel/mt76/patches/"
# Bundle custom package sources, but do not select them in minimal builds.
cp -a packages/. "$source_dir/package/custom/"

# Other historical diffs remain available, but are deliberately not
# included in the first minimal mt76-crash-fix validation build.
echo 'Pinned source and mt76 patch verified.'
