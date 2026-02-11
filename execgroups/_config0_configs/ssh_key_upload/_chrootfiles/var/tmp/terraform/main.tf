# Add a deploy key to the specified GitHub repository
resource "github_repository_deploy_key" "default" {
  title      = var.key_name
  repository = var.repository
  key        = base64decode(var.public_key_hash)
  read_only  = var.read_only
}

