module "subpj_retweet_checker" {
  source = "./modules/subpj_retweet_checker"

  tf_bucket = local.tf_bucket

  depends_on = [
    google_app_engine_application.app,
    google_project_service.services,
  ]
}
