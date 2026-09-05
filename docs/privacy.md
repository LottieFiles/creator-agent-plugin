# Privacy and data flow

The plugin sends only the tool input needed for the user request.

| Flow | Data | Control |
| --- | --- | --- |
| Host to Engine tools | Requested document operation and required identifiers | Inspect first; minimize input; host confirmation for writes. |
| Host to LottieFiles GraphQL | Query, variables, and account authorization context | Use variables; request minimum fields; scopes limit access. |
| Engine export | Requested format and approved destination | Confirm write or replacement destination. |
| Tool result to user | Minimum result, job state, warnings, and errors | Do not disclose tokens, variables, private content, or debug payloads. |

The package does not require users to put access tokens in source files. Follow the host’s secure credential storage method. See the [LottieFiles Privacy Policy](https://lottiefiles.com/page/privacy-policy) and [Terms and Conditions](https://lottiefiles.com/page/terms-and-conditions).
