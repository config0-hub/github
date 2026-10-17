# GitHub SSH Key Creation and Upload

## Description

This stack creates a new SSH key pair and uploads its public half to a GitHub repository as a read-only deploy key. EC2 generates the key pair in the `aws_default_region` of your AWS account and keeps the private half in SSM Parameter Store at `/ec2/keypair/<key_pair_id>`. The `ssh_key_pair` resource records `key_name`, `key_pair_id`, `public_key` and `private_key_ssm_path`, the name of that parameter. No Config0 state or record holds the private half. Removing the stack deletes the key pair, and AWS deletes the parameter with it.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| repo | GitHub repository for SSH key upload | &nbsp; |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| name | Alternative name configuration | null |
| key_name | SSH key identifier for resource access. Also the EC2 key pair name, unique per account and region | null |
| aws_default_region | AWS region of the key pair and of its SSM parameter | ap-northeast-1 |
| github_token | GitHub authentication token for repository access | null |

## Dependencies

### Substacks
- [config0-hub:::config0_core::tf_executor](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-hub/tf_executor/default)
- [config0-hub:::github::github_ssh_upload](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/github_ssh_upload)

### Execgroups
- [config0-hub:::aws::ssh_key_pair](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-hub/aws/ssh_key_pair/default)

### Scripts
- [config0-hub:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/scripts/config0-hub/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>