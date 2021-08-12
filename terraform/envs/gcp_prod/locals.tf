locals {
  project_name   = data.terraform_remote_state.bootstrap.outputs.project_name
  project_region = data.terraform_remote_state.bootstrap.outputs.project_ragion
  project_id     = data.google_project.project.number
  tf_bucket      = "${local.project_name}-terraform"
}
