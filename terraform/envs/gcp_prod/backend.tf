terraform {
  backend "gcs" {
    bucket = "pj-ray-kisaragi-prod-terraform"
    prefix = "tfstate"
  }
}

