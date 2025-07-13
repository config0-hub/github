# GitHub SSH Key Creation and Upload

## Description

This stack creates a new SSH key and uploads it to a specified GitHub repository. It handles the generation of the SSH key pair and automatic configuration of the key in the GitHub repository for secure access.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| repo | GitHub repository for SSH key upload | &nbsp; |
| stateful_id | Stateful ID for storing the resource code/state | _random |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| name | Alternative name configuration | null |
| key_name | SSH key identifier for resource access | null |
| schedule_id | ID of schedule associated with a stack/workflow | null |
| run_id | ID of a run for the instance of a stack/workflow | null |
| job_instance_id | ID of a job instance of a job in a schedule | null |
| job_id | ID of job in a schedule | null |
| github_token | GitHub authentication token for repository access | null |

## Dependencies

### Substacks
- [config0-publish:::new_ssh_key](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/new_ssh_key)
- [config0-publish:::github_ssh_upload](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/github_ssh_upload)

### Execgroups
None

### Shelloutconfigs
None

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>