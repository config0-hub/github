# GitHub SSH Key Upload

## Description
This stack uploads SSH public keys to GitHub repositories as deploy keys. It handles the secure storage, retrieval, and deployment of SSH keys to specified GitHub repositories with configurable access permissions.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| repo | Configuration for repo |  |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| key_name | SSH key identifier for resource access | None |
| name | Configuration for name | None |
| public_key_hash | 99checkme99 SSH public key in hashed/base64 format | None |
| public_key | SSH public key content | None |
| read_only | Configuration for read-only access to repo | "true" |

## Features
- Automatic retrieval of SSH public keys from config0 resources if not explicitly provided
- Support for read-only or read-write access to repositories
- GitHub authentication via token for secure API access
- Terraform-based deployment for consistent infrastructure management
- Integration with config0 resource management

## Dependencies

### Substacks
- [config0-publish:::tf_executor](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/tf_executor)

### Execgroups
- [config0-publish:::github::ssh_key_upload](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/github/ssh_key_upload)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.