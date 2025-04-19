# GitHub Pull Request Creator

A simple OpenTofu module to create GitHub pull requests programmatically.

## Description

This module allows you to create GitHub pull requests using OpenTofu. It can be useful for automation workflows, CI/CD pipelines, or any scenario where you need to programmatically create pull requests.

## Requirements

- OpenTofu >= 1.8.0
- GitHub Provider >= 5.0.0

## Usage

```hcl
module "github_pr" {
  source         = "./github-pr-creator"
  
  repository     = "my-repo"
  base_branch    = "main"
  feature_branch = "feature/new-feature"
  body_b64       = base64encode("This PR adds the new feature")
}
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| repository | The name of the GitHub repository where the PR will be created | string | "private-test" | no |
| base_branch | The target branch for the pull request (where changes will be merged into) | string | "main" | no |
| feature_branch | The source branch for the pull request (containing the changes to be merged) | string | "dev" | no |
| body_b64 | Base64 encoded content for the pull request body | string | n/a | yes |

## Alternative Usage

If you prefer to use a file for the PR body content, uncomment the `local_file` data source and related configuration in the module.

```hcl
module "github_pr" {
  source         = "./github-pr-creator"
  
  repository     = "my-repo"
  base_branch    = "main"
  feature_branch = "feature/new-feature"
  # Use a file for PR body instead of base64 encoded string
  # Uncomment the local_file data source in the module
}
```

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.