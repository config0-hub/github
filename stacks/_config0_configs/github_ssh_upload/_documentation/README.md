**Description**

  - The GITHUB_TOKEN needs to be injected by the Config0 platform as an inputvars

  - The stack uploads ssh public key to github.
  - The stack requires name or key_name of the public key
  - The stack will first look for the public_key in the variables
  - The stack will second look for the public_key in the Config0's inputvars (in example below input-ssh-public-key)
  - The stack will thirdly look for the public_key in the Config0's resources

**Required**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| repo   | github repository | string   | None         |

**Optional**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| key_name   | name of the ssh key                 | string   | None         |
| name   | name of the ssh key                 | string   | None         |
| public_key   | public_key in base64                | string   | None         |
| read_only   | read_only (true/false)               | boolean   | true         |

**Sample entry**

```
infrastructure:
   ssh_upload:
       stack_name: config0-hub:::github_ssh_upload
       arguments:
          key_name: config0-test-github-key
          repo: config0-private-test
       inputvars:
           - reference: github-token
             orchestration: true
           - reference: input-ssh-public-key
             orchestration: true
```
