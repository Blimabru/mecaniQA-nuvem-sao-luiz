

**Contexto Inicial do Produto**

Os projetos deste programa serão implementados em grupos de 5 membros. Exceções devem ser comunicadas ao orientador e registradas e autorizadas por ele. Cada time vai ter um nome conforme planilha, e os nomes dos times serão sorteados no nosso primeiro encontro.

A MecâniQA Tech é uma startup que fornece um sistema SaaS de gestão e diagnóstico automotivo para oficinas mecânicas. A nossa aplicação principal é desenvolvida em Java, gerenciando dados transacionais com um banco de dados relacional MySQL e utilizando Redis (banco de dados NoSQL) para o armazenamento de dados em alta velocidade. No cenário atual, a infraestrutura sofre para escalar e os recursos são frequentemente esgotados. Neste primeiro desafio, sua equipe atuará como Engenheiros Cloud/DevOps, orquestrando a saída de uma infraestrutura local instável para uma fundação resiliente e conteinerizada.

**Objetivos da Sprint**

* Compreender os conceitos da Camada Virtual e dominar a criação do Dockerfile isolado para a aplicação Java, para o banco de dados MySQL e para o Redis.

* Implementar a orquestração local através da criação do docker-compose.yml, configurando redes em containers (DNS interno) e garantindo a persistência de dados.

* Desenhar a infraestrutura de forma declarativa e iniciar a gestão de ambientes utilizando a infraestrutura como código (Terraform).

* Introduzir a Camada de Controle realizando a gestão de Pods, Deployments e Services com o Kubernetes (K8s) e o monitoramento utilizando o K9s.

**Especificação do Produto Final:** 

Vocês deverão entregar um repositório funcional que atenda rigorosamente aos seguintes requisitos técnicos de infraestrutura:

* **Empacotamento de Serviços:** O código deve conter os arquivos Dockerfile devidamente construídos para levantar as imagens independentes do back-end em Java, do MySQL e do Redis.

* **Orquestração e Redes:** Um arquivo docker-compose.yml que demonstre a capacidade de rodar todo o ecossistema simultaneamente com persistência de dados estruturada.

* **Gestão de Estado:** Os manifestos declarativos nativos do Kubernetes e a configuração inicial de provisionamento utilizando Terraform.

**Entrega do Código:** 

* O projeto deve ser versionado e entregue no repositório de cada equipe. O nome do repositório deve seguir o padrão: mecaniQA-nuvem-\<nome\_do\_time\>. Exemplo: mecaniQA-nuvem-sao-paulo, para um time que se chama São Paulo. 

* Crie um [READ.me](http://READ.me) do repositório com o contexto do trabalho e o nome dos membros do time. 

* Atualize a tabela de [Equipes](https://docs.google.com/spreadsheets/d/1UGtPZvEjjFqz0Uz1LnYi6u_EKi-XdnaGT8TQzumin5k/edit?usp=sharing) com o link do seu repositório. Não esqueça de adicionar o professor ao repositório. Você pode enviar o convite para o **nickname: lasilva**. 

* **Repositórios com nomes fora do padrão não serão avaliados.** 

* **A ENTREGA QUE VAI SER AVALIADA VAI SER A QUE ESTIVER NA BRANCH MAIN ATÉ A DATA LIMITE.** 

**Apresentação:**

* Vocês devem elaborar uma apresentação no [Modelo de Apresentação](https://docs.google.com/presentation/d/1HayWJi__y8W4vx_2zcrZtigDn02aBJdoKDkKZiKsjf0/edit?usp=sharing). 

* As apresentações serão realizadas APENAS para o professor. 

* A apresentação também precisa ser versionada no repositório com o seguinte padrão de nome: mecaniQA\_oat1\_\<nome\_da\_equipe\>.pdf. 

* Além do versionamento, a apresentação deve ser entregue no blackboard no formulário: [Formulário de Submissão de Apresentação](https://ftc.blackboard.com/ultra/courses/_99028_1/assessment/test/_12375477_1?gradeitemView=details).

**Avaliação:** 

Neste semestre, vamos introduzir algumas nomenclaturas que serão importantes ao longo do processo avaliativo e formativo de vocês. Vocês serão solicitados, a cada período de tempo, aproximadamente entre 3 e 4 semanas, uma entrega de valor. Nós chamamos essas solicitações de **demandas**. Vocês atuarão em equipe para entregar o resultado dessas **demandas** que vem da área de produto. Quem especifica o produto é conhecido, em ambientes que utilizam metodologias ágeis, de **Product Owner**, ou simplesmente, **PO (lê-se Pi-Ou)**. A entrega de valor realizada ao final de cada demanda vai ser chamada de **Entregável**.  Em geral, os **entregáveis** são arquivos de **código fonte** que realizam uma atividade. Nós vamos usar siglas para nos referimos aos entregáveis, por exemplo: **Entregável 1 \- E1, Entregável 2 \- E2,** e assim por diante. 

A cada entrega, vocês produzirão uma apresentação oral que será executada após a data da entrega. Nessa avaliação, vocês terão que apresentar o contexto do que foi desenvolvido e serão questionados pelo professor. A avaliação oral é um **peso** que vai ser utilizado para ponderar o valor obtido no entregável. Além disso, vocês serão avaliados processualmente nas Sessões Tutoriais (ST). Cada ST equivale a 1 ponto e sua quantidade varia conforme a Sprint. Deste modo, o valor final do entregável será: 

VF\_E \= (AO \* E ) / 10 \+ ST 

onde: 

**VF\_E** é o Valor Final do Entregável 

**AO** \- Apresentação Oral 

**E** \- Valor do Entregável 

**ST** \- Sessão Tutorial

**Observações importantes:** 

1. Apresentações fora do padrão estabelecido serão pontuadas com zero.   
2. As apresentações devem ser realizadas no máximo de 7 minutos.   
3. **APENAS UM MEMBRO DA EQUIPE VAI REALIZAR A APRESENTAÇÃO. O MEMBRO DA EQUIPE SERÁ ESCOLHIDO PELO PROFESSOR NO DIA DA APRESENTAÇÃO.**   
4. Se a equipe não apresentar, o valor da entrega será zero.   
5. Se um membro da equipe faltar a apresentação no dia ficará com 30% da nota de apresentação da equipe. **Para faltas não justificadas.**  
6. Apresentações não versionadas serão pontuados com zero.   
   

**Pontuação:** 

| Atividade | Peso |
| :---- | :---- |
| **Apresentação** | 6 |
| **Entregável 1** | 10 |

| Atividade | Nota |
| :---- | :---- |
| **Entregável 1** | 6 pontos |
| **Sessões Tutoriais** | 4 pontos |

**Prazos:**

| Atividade | Data |
| :---- | :---- |
| **OAT 1 \- Entregável** | 19/09/2026 |
| **Apresentação** | até 14/10/2026 |

**BAREMA:**

[**BAREMA DA ATIVIDADE 1 \- DOCKER, DOCKER-COMPOSE, K8S**](https://docs.google.com/spreadsheets/d/1b2qX-RW9jgum4VJBwLz66hnt8XQyRIUeG1smQz3a2mM/edit?usp=sharing)