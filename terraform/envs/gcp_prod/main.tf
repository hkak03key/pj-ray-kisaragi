module "subpj_retweet_checker" {
  source = "./modules/subpj_retweet_checker"

  tf_bucket = local.tf_bucket
}
