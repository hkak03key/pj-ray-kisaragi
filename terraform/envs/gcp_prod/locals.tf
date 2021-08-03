locals {
  project_name = data.terraform_remote_state.bootstrap.outputs.project_name
  project_id   = data.google_project.project.number
}
