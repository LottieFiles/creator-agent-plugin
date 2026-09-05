# Submission checklist

## Package

- [ ] Run the content generator and confirm generated copies match `content/skills` and `content/assets`.
- [ ] Validate manifests, metadata, and version against the release tag.
- [ ] Replace contract reconciliation notes with the released public fixture path and hash.
- [ ] Replace schema placeholders only with fields confirmed by a public schema.
- [ ] Confirm every public URL resolves from an external network.
- [ ] Verify the package contains no secrets, private paths, user data, debug payloads, or proprietary schema.

## Human and administrator gates

- [ ] Product owner approves listing copy, prompts, and examples.
- [ ] LottieFiles administrator approves GraphQL scopes and mutation behavior.
- [ ] Security owner approves the threat model and data-flow notes.
- [ ] Legal and brand owner approves license, trademarks, links, and asset provenance.
- [ ] Marketplace administrator approves the final package and directory submission.
- [ ] Release manager records the package version, commit, checksum, and rollback target.

## Live acceptance

- [ ] Test each positive and negative case in the target host.
- [ ] Confirm the host shows write and delete confirmation.
- [ ] Confirm OAuth and revoked-scope behavior.
- [ ] Confirm partial GraphQL errors retain safe data and report the failure.
- [ ] Confirm an async job succeeds, fails, and cancels as expected.
- [ ] Confirm support contact and privacy links in the published listing.
