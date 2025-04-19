# GitHub Deploy Key Module

This OpenTofu module creates a deploy key for a GitHub repository. Deploy keys are SSH keys that grant access to a single repository, allowing automated systems to pull or push code without using a personal account.

## Requirements

- OpenTofu >= 1.8.0
- GitHub Provider ~> 5.0

## Usage

```hcl
module "github_deploy_key" {
  source          = "./path/to/module"
  key_name        = "my-deploy-key"
  public_key_hash = "base64_encoded_public_key"
  repository      = "my-repository"
  read_only       = true
}
```

## Input Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| key_name | The title of the deploy key to be created | string | n/a | yes |
| public_key_hash | The base64 encoded public key hash to use as the deploy key | string | n/a | yes |
| read_only | Determines if the deploy key has read-only access or read-write access | bool | true | no |
| repository | The GitHub repository where the deploy key will be added | string | "config0-private-test" | no |

## Outputs

| Name | Description |
|------|-------------|
| etag | The ETag of the deploy key resource |
| repository | The name of the repository where the deploy key was added |
| title | The title/name of the deploy key |

## How to Generate a Deploy Key

1. Generate an SSH key pair:
   ```
   ssh-keygen -t ed25519 -f deploy_key -C "deploy key for repository"
   ```

2. Base64 encode the public key:
   ```
   cat deploy_key.pub | base64
   ```

3. Use the encoded string as the value for `public_key_hash`

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.