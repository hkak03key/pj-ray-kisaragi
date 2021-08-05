data "terraform_remote_state" "bootstrap" {
  backend = "local"

  config = {
    path = ".bootstrap_resources/terraform.tfstate"
  }
}

