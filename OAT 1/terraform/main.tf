# Terraform para provisionamento inicial da infraestrutura local da MecaniQA.
#
# Este arquivo define a base de infraestrutura como código para provisionar a
# rede Docker, os volumes persistentes e os containers do MySQL e do Redis.
# O objetivo é representar a camada de provisionamento inicial do ambiente,
# permitindo a reprodução automatizada de recursos locais em cenários de teste.
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

# Rede interna utilizada para comunicação entre os serviços.
# A infraestrutura de rede deve manter os containers isolados da rede externa,
# permitindo que o fluxo de dados ocorra apenas entre os serviços da aplicação.
resource "docker_network" "mecaniqa_network" {
  name = "mecaniqa-network"
}

# Volume persistente para os dados do banco de dados MySQL.
# A persistência evita a perda de informações em reinicializações do contêiner,
# preservando o estado de dados da aplicação.
resource "docker_volume" "mysql_data" {
  name = "mecaniqa_mysql_data"
}

# Volume persistente para os dados do Redis.
# O cache em memória pode ser reinicializado sem perda de dados em cenários de
# laboratório, desde que o armazenamento persistente seja mantido.
resource "docker_volume" "redis_data" {
  name = "mecaniqa_redis_data"
}

# Definição do container do MySQL.
# Este recurso representa o banco de dados principal da aplicação e deve manter
# as configurações mínimas de acesso, persistência e rede local.
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

# Definição do container do Redis.
# Este recurso representa o mecanismo de cache em memória e deve ser executado em
# rede interna para manter o isolamento da infraestrutura local.
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

# Imagem oficial do MySQL 8.0.
# A utilização da imagem oficial reduz riscos de incompatibilidade e mantém a
# configuração mínima recomendada pela documentação do banco.
resource "docker_image" "mysql" {
  name = "mysql:8.0"
}

# Imagem oficial leve do Redis.
# A imagem baseada em Alpine é adequada para reduzir o peso do contêiner e manter
# o ambiente operacional enxuto para fins de laboratório.
resource "docker_image" "redis" {
  name = "redis:alpine"
}
