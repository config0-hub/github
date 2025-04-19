# GitHub Repository Webhook Terraform Module

This Terraform module creates a webhook for a GitHub repository. It allows you to define webhook configuration including URL, content type, secret, and events that trigger the webhook.

## Requirements

- OpenTofu >= 1.8.0
- GitHub Provider >= 5.0.0

## Usage

```hcl
module "github_webhook" {
  source = "path/to/module"

  repository   = "my-repo"
  url          = "https://webhook.example.com/endpoint"
  events       = "push,pull_request"
  secret       = "my-webhook-secret"
  content_type = "json"
}
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| url | The URL to which the payloads will be delivered | string | n/a | yes |
| repository | The name of the GitHub repository to add the webhook to | string | `"config0-private-test"` | no |
| events | Comma-separated list of GitHub events to trigger the webhook | string | `"push,pull_request"` | no |
| secret | Secret key used to sign the webhook payload | string | `"secret123"` | no |
| content_type | The content type for the payload (json or form) | string | `"json"` | no |
| insecure_ssl | Whether to allow insecure SSL connections to the webhook URL | bool | `true` | no |
| active | Whether the webhook is active | bool | `true` | no |

## Outputs

| Name | Description |
|------|-------------|
| webhook_id | The ID of the created webhook |
| etag | The ETag of the webhook |
| events | The list of events that trigger the webhook |
| url | The URL of the webhook (sensitive) |
| repository | The repository where the webhook is installed |

## Notes

- The webhook secret is used to secure your webhook payloads. It's recommended to use a strong random value.
- Setting `insecure_ssl` to `true` is not recommended for production environments.
- Webhook events are provided as a comma-separated string and internally converted to a list.

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.