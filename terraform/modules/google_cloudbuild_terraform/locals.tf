locals {
  terraform_docker_image = "hashicorp/terraform:${var.terraform_docker_image_ver}"

  timeout = {
    preparing = 60
    main      = 600
  }

  proc_args = {
    plan  = "plan -lock=false"
    apply = "apply -auto-approve"
  }

  steps = [
    {
      id      = "check fmt"
      dir     = var.terraform_check_fmt_dir != null ? var.terraform_check_fmt_dir : var.terraform_exec_dir
      args    = "fmt -diff -check -recursive"
      timeout = local.timeout["preparing"]
    },
    {
      id      = "terraform init"
      dir     = var.terraform_exec_dir
      args    = "init"
      timeout = local.timeout["preparing"]
    },
    {
      id      = "terraform variable"
      dir     = var.terraform_exec_dir
      args    = "validate"
      timeout = local.timeout["preparing"]
    },
    {
      id      = "terraform ${var.proc}"
      dir     = var.terraform_exec_dir
      args    = local.proc_args[var.proc]
      timeout = local.timeout["main"]
    },
  ]
}

