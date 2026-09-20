# Terraform para provisionamento inicial da infraestrutura local da MecaniQA.
# Este arquivo cria a rede Docker, os volumes de persistência e os containers
# do MySQL e do Redis para representar a base de Infraestrutura como Código.
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

# Rede interna usada para comunicação entre os serviços
resource "docker_network" "mecaniqa_network" {
  name = "mecaniqa-network"
}

# Volume persistente para dados do banco MySQL
resource "docker_volume" "mysql_data" {
  name = "mecaniqa_mysql_data"
}

# Volume persistente para dados do Redis
resource "docker_volume" "redis_data" {
  name = "mecaniqa_redis_data"
}

# Container do MySQL
resource "docker_container" "db" {
  name  = "mecaniqa-db"
  image = docker_image.mysql.image_id

  env = [
    "MYSQL_DATABASE=mecaniqa",
    "MYSQL_ROOT_PASSWORD=root"
  ]

  ports {
    internal = 3306
    external = 3306
  }

  volumes {
    volume_name    = docker_volume.mysql_data.name
    container_path = "/var/lib/mysql"
  }

  networks_advanced {
    name = docker_network.mecaniqa_network.name
  }
}

# Container do Redis
resource "docker_container" "redis" {
  name  = "mecaniqa-redis"
  image = docker_image.redis.image_id

  ports {
    internal = 6379
    external = 6379
  }

  volumes {
    volume_name    = docker_volume.redis_data.name
    container_path = "/data"
  }

  networks_advanced {
    name = docker_network.mecaniqa_network.name
  }
}

# Imagem oficial do MySQL 8.0
resource "docker_image" "mysql" {
  name = "mysql:8.0"
}

# Imagem oficial leve do Redis
resource "docker_image" "redis" {
  name = "redis:alpine"
}
