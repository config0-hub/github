**Description**

  - The stack generates ssh_key and uploads it to github.

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| key_name   | name of the ssh key                 | string   | None         |
| repo   | github repository | string   | None         |


**Sample entry**

```
infrastructure:
   ssh_upload:
       stack_name: config0-hub:::new_github_ssh_key
       arguments:
          key_name: config0-test-github-key
          repo: config0-private-test
       inputvars:
           - reference: github_token
             orchestration: true
```
