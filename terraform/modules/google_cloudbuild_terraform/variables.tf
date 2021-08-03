variable "name" {
  description = "the name of cloudbuild trigger."
  type        = string
}

variable "terraform_docker_image_ver" {
  description = "the terraform docker image version."
  type        = string
}

variable "terraform_exec_dir" {
  description = "the exec directory of terraform."
  type        = string
}

variable "terraform_check_fmt_dir" {
  description = "the target directory of \"terraform fmt -recursive\". if not specify, using var.terraform_exec_dir ."
  type        = string
  default     = null
}

variable "github" {
  description = "the configure of google_cloudbuild_trigger.github ."
  type = object({
    owner        = string
    name         = string
    pull_request = optional(map(any)) # same as pull_request block. required eather pull_request or push
    push         = optional(map(any)) # same as push block. required eather pull_request or push
  })
}

variable "proc" {
  description = "the proc: \"plan\" or \"apply\" ."
  type        = string
  validation {
    condition     = contains(["plan", "apply"], var.proc)
    error_message = "The proc value must be any one of [\"plan\", \"apply\"]."
  }
}

