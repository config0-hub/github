resource "github_repository" "default" {
  name        = var.repository
  description = "This is a repo ${var.repository} created using Terraform"

  visibility = var.visibility
  auto_init  = true

  has_issues             = var.has_issues
  has_projects           = var.has_projects
  has_wiki               = var.has_wiki
  delete_branch_on_merge = var.delete_branch_on_merge
}

resource "github_branch" "default" {
  repository = github_repository.default.name
  branch     = var.default_branch
}

resource "github_branch_default" "default" {
  repository = github_repository.default.name
  branch     = github_branch.default.branch
}

/*
#The below requires GitHub Pro/Enterprise
#Uncomment if you have the appropriate GitHub plan
resource "github_branch_protection" "default" {
repository_id    = github_repository.default.node_id
pattern          = var.default_branch
allows_deletions = true
*/

