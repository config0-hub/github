resource "github_repository_pull_request" "default" {
  base_repository = var.repository
  base_ref        = var.base_branch
  head_ref        = var.feature_branch
  title           = "PR for ${var.feature_branch} to ${var.base_branch}"
  body            = base64decode(var.body_b64)
}

