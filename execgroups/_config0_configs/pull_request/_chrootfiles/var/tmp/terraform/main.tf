provider "github" {}

# if you want to get the body from a file instead
#data "local_file" "default" {
#  filename = "/tmp/output"
#}

resource "github_repository_pull_request" "default" {
  base_repository = var.repository
  base_ref        = var.base_branch
  head_ref        = var.feature_branch
  title           = "PR for ${var.feature_branch} to ${var.base_branch}"
  body            = base64decode(var.body_b64)
  #body            = data.local_file.default.content
}
