# GitHub Webhook Stack

## Description
This stack creates a GitHub webhook for a repository. It allows you to set up automated notifications to be sent from GitHub to a specified URL when certain events occur in your repository.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| name | Configuration for name | &nbsp; |
| url | Webhook destination URL | &nbsp; |
| repo | Configuration for repo | &nbsp; |
| secret | Configuration for secret | _random |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| insecure_ssl | Configuration for insecure SSL | true |
| active | Configuration for whether the webhook is active | true |
| content_type | Configuration for content type | json |
| events | Events that trigger the webhook | push,pull_request |

## Dependencies

### Substacks
- [config0-publish:::tf_executor](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/tf_executor/default)

### Execgroups
- [config0-publish:::github::add_webhook](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/add_webhook/default)

### Shelloutconfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>