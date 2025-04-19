# GitHub Repository Terraform Module

This module creates and configures a GitHub repository with basic settings.

## Features

- Creates a new GitHub repository
- Sets up a default branch
- Configures repository settings (issues, projects, wiki, etc.)
- Optional branch protection (requires GitHub Pro/Enterprise)

## Usage

```hcl
module "github_repo" {
  source = "./path/to/module"
  
  repository             = "my-awesome-repo"
  visibility             = "private"
  has_issues             = true
  has_projects           = false
  has_wiki               = false
  delete_branch_on_merge = true
  default_branch         = "main"
}
```

## Requirements

- OpenTofu 1.8.8 or later
- GitHub provider 5.0 or later
- GitHub account with appropriate permissions

## Input Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| repository | Name of the GitHub repository to create | string | "private-test" | no |
| visibility | Visibility of the repository (private, public, or internal) | string | "private" | no |
| has_issues | Enable GitHub issues for this repository | bool | true | no |
| has_projects | Enable GitHub projects for this repository | bool | false | no |
| has_wiki | Enable GitHub wiki for this repository | bool | false | no |
| delete_branch_on_merge | Automatically delete head branch after a pull request is merged | bool | true | no |
| default_branch | Name of the default branch for this repository | string | "main" | no |

## Outputs

This module does not provide outputs. Add outputs as needed for your specific use case.

## Notes

- The branch protection resource is commented out as it requires GitHub Pro or Enterprise.
- If you need branch protection, uncomment the relevant section and ensure you have the appropriate GitHub plan.

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.