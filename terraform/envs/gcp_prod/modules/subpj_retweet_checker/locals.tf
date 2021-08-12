locals {
  module_name = replace(basename(path.module), "_", "-")
  region      = data.google_client_config.this.region
  project_id  = data.google_project.project.number
}
