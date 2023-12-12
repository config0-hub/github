provider "github" {}

# Add a deploy key
# we have used key_name for title to make it consistent with ssh keys in general

resource "github_repository_deploy_key" "default" {
  title      = var.key_name
  repository = var.repository
  key        = base64decode(var.public_key_hash)
  read_only  = var.read_only
}
