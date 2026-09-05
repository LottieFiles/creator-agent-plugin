# LottieFiles Creator

LottieFiles Creator is a public agent plugin package for animation document workflows and approved LottieFiles account access. It supplies task skills, safe examples, and submission material for MCP-capable hosts.

Use it to:

- Create, edit, inspect, export, and review animation documents with Engine tools.
- Search and inspect LottieFiles resources through `lf_graphql`.
- Make account changes only with explicit user intent, host confirmation, and approved scopes.

The package does not claim a live directory listing or public endpoint. Read [installation guidance](docs/installation.md) before you connect it.

## Safe use

1. Discover the installed tool contract and GraphQL schema before an operation.
2. Request the minimum fields and use variables for GraphQL values.
3. Paginate bounded lists.
4. Inspect a resource before you change it.
5. Confirm the target and effect before a write, delete, export, or overwrite.
6. Keep tokens and variables out of logs.
7. Treat GraphQL `data` with `errors` as partial data.

Full LottieFiles GraphQL access is intentional. The connected account scopes still define what the tool can access. The plugin never bypasses scopes.

## Contents

- [Skills](content/skills/)
- [Examples](examples/)
- [Installation matrix](docs/installation.md)
- [Privacy and data flow](docs/privacy.md)
- [Security and threat model](docs/security.md)
- [Versioning, release, and rollback](docs/release.md)
- [Research and support status](docs/research.md)
- [Submission materials](submission/)

## Support and legal

- [LottieFiles](https://lottiefiles.com)
- [LottieFiles Help Center](https://help.lottiefiles.com)
- [Privacy Policy](https://lottiefiles.com/page/privacy-policy)
- [Terms and Conditions](https://lottiefiles.com/page/terms-and-conditions)
- [Brand assets](https://lottiefiles.com/brand-assets)

See [SUPPORT.md](SUPPORT.md), [SECURITY.md](SECURITY.md), and [CONTRIBUTING.md](CONTRIBUTING.md) for project processes.

## License

This package uses the [MIT License](LICENSE).
