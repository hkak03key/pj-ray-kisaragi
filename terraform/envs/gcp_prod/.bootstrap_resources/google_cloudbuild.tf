module "google_cloudbuild_tf_plan_for_pr" {
  source                     = "../../../modules/google_cloudbuild_terraform"
  name                       = "tf-plan-for-pr"
  terraform_docker_image_ver = "1.0.2"
  terraform_check_fmt_dir    = "terraform"
  terraform_exec_dir         = "terraform/envs/gcp_prod"
  github = {
    owner = "hkak03key"
    name  = "pj-ray-kisaragi"
    pull_request = {
      branch          = ".*"
      comment_control = "COMMENTS_ENABLED_FOR_EXTERNAL_CONTRIBUTORS_ONLY"
    }
  }
  proc = "plan"

  depends_on = [
    google_project_service.services,
  ]
}

module "google_cloudbuild_tf_apply_main_branch" {
  source                     = "../../../modules/google_cloudbuild_terraform"
  name                       = "tf-apply-main-branch"
  terraform_docker_image_ver = "1.0.2"
  terraform_check_fmt_dir    = "terraform"
  terraform_exec_dir         = "terraform/envs/gcp_prod"
  github = {
    owner = "hkak03key"
    name  = "pj-ray-kisaragi"
    push = {
      branch = "^main$"
    }
  }
  proc = "apply"

  depends_on = [
    google_project_service.services,
  ]
}

resource "google_project_iam_binding" "cloudbuild" {
  project = local.project_id
  role    = "roles/admin"

  members = [
    "serviceAccount:${local.project_id}@cloudbuild.gserviceaccount.com",
  ]
}
