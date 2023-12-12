**Description**

  - The creates a webhook to designated url on github.

**Required**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| name   | name of the webhook | string   | None         |
| repo   | github repository | string   | None         |
| url   | the designated url for the webook | string   | None         |
| secret   | the secret to verify the webook | [auto-generated-random]   | None         |

**Optional**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| insecure_ssl   | allowed insecure ssl connection | true   | None         |
| active   | webhook is active or not | true   | None         |
| content_type   | content_type of webhook | json   | None         |
| events   | events of to invoke webhook | push,pull_request   | None         |

**Sample entry**

```
infrastructure:
   ssh_upload:
       stack_name: config0-hub:::github_webhook
       arguments:
          name: config0-private-test-webhook
          repo: config0-private-test
          url: https://app-api.elasticedev.io/webhook
       inputvars:
           - reference: github-token
             orchestration: true
```
