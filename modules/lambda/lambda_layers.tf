# create zip file from requirements.txt. Triggers only when the file is updated
resource "random_string" "random_suffix" {
  for_each = { for key, value in var.lambda_layer_list : value.name => value }
  length   = 8
  special  = false
  upper    = false
  keepers = {
    requirements = filesha1("${path.module}/layers/${each.value.name}/requirements.txt")
  }
}

resource "null_resource" "lambda_layer" {
  for_each = { for key, value in var.lambda_layer_list : value.name => value }

  triggers = {
    requirements = filesha1("${path.module}/layers/${each.value.name}/requirements.txt")
  }

  provisioner "local-exec" {
    command = <<EOT
      echo "⚡ Running build_layer.sh for ${each.value.name}..."
      cd ${path.module}/layers/${each.value.name}
      ./build_layer.sh
      mv PythonRequirements.zip PythonRequirements-${random_string.random_suffix[each.value.name].result}.zip
    EOT
  }
}


# upload zip file to s3
resource "aws_s3_object" "lambda_layer_zip" {
  for_each = { for key, value in var.lambda_layer_list : value.name => value }

  bucket     = aws_s3_bucket.lambda_s3.bucket
  key        = "layers/${each.value.name}/PythonRequirements-${random_string.random_suffix[each.value.name].result}.zip"
  source     = "${path.module}/layers/${each.value.name}/PythonRequirements-${random_string.random_suffix[each.value.name].result}.zip"
  depends_on = [null_resource.lambda_layer] # triggered only if the zip file is created
}

# create lambda layer from s3 object
resource "aws_lambda_layer_version" "this" {
  for_each = { for key, value in var.lambda_layer_list : value.name => value }

  s3_bucket           = aws_s3_bucket.lambda_s3.bucket
  s3_key              = aws_s3_object.lambda_layer_zip[each.value.name].key
  layer_name          = "${var.common.project_name}_${each.value.name}-PythonRequirements-${random_string.random_suffix[each.value.name].result}-lambda-layer-01" # Change this if increment
  compatible_runtimes = ["${var.runtime}"]
  skip_destroy        = true
  depends_on          = [aws_s3_object.lambda_layer_zip] # triggered only if the zip file is uploaded to the bucket
}


