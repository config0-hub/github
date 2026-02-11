# Output variables to provide information about the created deploy key
output "etag" {
  description = "The ETag of the deploy key resource"
  value       = github_repository_deploy_key.default.etag
}

output "repository" {
  description = "The name of the repository where the deploy key was added"
  value       = github_repository_deploy_key.default.repository
}

output "title" {
  description = "The title/name of the deploy key"
  value       = github_repository_deploy_key.default.title
}