# Versioning, release, and rollback

Use semantic versioning.

- Increase PATCH for compatible fixes and documentation corrections.
- Increase MINOR for compatible capabilities.
- Increase MAJOR for a breaking package or tool-contract change.

## Release procedure

1. Generate platform copies from canonical `content/skills` and `content/assets`.
2. Validate generated output, metadata, links, and public-contract synchronization.
3. Run the release test suite and the submission test cases in each supported host.
4. Record the tag, commit, package checksum, public endpoint, and contract fixture hash.
5. Publish only after the checklist human and administrator gates pass.
6. Publish the directory entry only after the package is available from its public source.

## Contract synchronization

Treat the released public tool and GraphQL contracts as versioned inputs. Before each release:

1. Compare the contract fixture with skill references and examples.
2. Replace only verified placeholders.
3. Add or update test fixtures for changed result shapes and error behavior.
4. Document the contract version and hash in the release record.
5. Block publication if a tool name, argument, result, scope, or security rule cannot be confirmed.

## Rollback

1. Disable the affected directory listing or release channel.
2. Restore the last verified package version and endpoint configuration.
3. Revoke or narrow credentials if the incident involves access control.
4. Tell users what changed, what data may be affected, and the safe upgrade or removal action.
5. Preserve release evidence and add a regression test before republishing.
