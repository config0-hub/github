# GitHub Webhook Stack

## Description
This stack creates a GitHub webhook for a repository. It allows you to set up automated notifications to be sent from GitHub to a specified URL when certain events occur in your repository.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| name | Configuration for name | |
| url | Webhook destination URL | |
| repo | Configuration for repo | |
| secret | Configuration for secret | _random |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| insecure_ssl | Configuration for insecure SSL | true |
| active | Configuration for whether the webhook is active | true |
| content_type | Configuration for content type | json |
| events | Events that trigger the webhook | push,pull_request |

## Features
- Creates a GitHub repository webhook with customizable events and settings
- Supports configurable secret for webhook security
- Allows specifying webhook content type and event triggers
- Supports enabling/disabling the webhook

## Dependencies

### Substacks
- [config0-publish:::tf_executor](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/tf_executor)

### Execgroups
- [config0-publish:::github::add_webhook](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/github/add_webhook)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.