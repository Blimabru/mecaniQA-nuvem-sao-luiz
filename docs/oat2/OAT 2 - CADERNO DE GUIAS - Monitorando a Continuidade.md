

| PROBLEMA: | Monitorando a Continuidade | DATA: | 07/10/2026 |
| :---- | :---- | :---- | :---- |
| **PILOTO (A):** | Keven Moraes Patricio | **COPILOTO (A):** | Tiago Ferraz de Novais |
| **QA:** | Bruno Moreira Lima | **ARQUITETO (A):** | Claudio Pales Costa |
| **SCRUM MASTER:** | Gabriel Honorato Santos Ferraz |  |  |

Objetivo: Realizar um brainstorming de soluções e arquiteturas para monitorar a saúde das aplicações e resolver o desafio do tráfego massivo de IoT (Infraestrutura e Segurança) das oficinas mecânicas.

Instrução: O Scrum Master tem 10 minutos para guiar a equipe nestas pesquisas e preencher o *board* (Fatos, Questões e Ideias). O Arquiteto anota as respostas diretas, estrutura a solução técnica e redige o Relatório da Sessão.

🧠 Brainstorm Investigativo (Pesquisem e debatam\!)

* A Cegueira Operacional: Atualmente, o cluster da MecâniQA Tech opera como uma "caixa preta" e a equipe de Engenharia não tem visibilidade sobre a saúde das aplicações. O que significa, na prática, introduzir o conceito de observabilidade e métricas nesse ambiente?

  * Decisão da Equipe: Vamos a partir disso criar dashboard com o grafana prometheus para deixar as informações mais fáceis de serem interpretadas e compreendidas.

* A Stack de Monitoramento: Para preparar o ambiente, precisaremos utilizar ferramentas padrão de mercado. Como o Prometheus e o Grafana se comunicam para transformar dados brutos do simulador de sensores IoT (Python) em informações visuais?

  * Decisão da Equipe: O prometheus seria o banco de dados que coleta as informações dos demais dispositivos ou sistemas, ja o Grafana cria paineis visuais (famosas dashboards) para exibir os dados do prometheus de forma visual

**BRAINSTORM GUIADO** 

*Instrução: Debatam rapidamente as perguntas abaixo consultando os materiais. O Arquiteto deve digitar a decisão da equipe diretamente nos espaços em branco deste documento.*

1\. O Desafio do Tráfego: A MecâniQA Tech recebe milhares de leituras simultâneas de sensores IoT (temperatura do motor, falhas elétricas) às 08:00 e às 17:00. Por que um modelo de monitoramento tradicional, focado apenas em checar se o servidor "está ligado", é insuficiente para garantir a estabilidade nesses horários de pico?

######  **ENTREGA DO ENCONTRO:**

Objetivo Prático: Iniciar o Projeto de Métricas subindo a stack de monitoração (Prometheus) e realizando a instrumentação da aplicação base (simulador de sensores IoT em Python).

Passo a Passo para o Piloto e Copiloto:

1. Modificar o código fonte em Python inserindo as bibliotecas necessárias para expor as métricas da aplicação.  
2. Escrever os manifestos ou configurações necessárias (arquivos YAML) para realizar o deploy funcional do Prometheus no cluster Kubernetes.  
3. Comitar a versão inicial do código instrumentado e dos manifestos na branch *main* do repositório da equipe (seguindo o padrão mecaniQA-\<nome\_do\_time\>).

![][image1]

| PROBLEMA: | Monitorando a Continuidade | DATA: | 14/10/2026 |
| :---- | :---- | :---- | :---- |
| **PILOTO (A):** |  | **COPILOTO (A):** |  |
| **QA:** |  | **ARQUITETO (A):** |  |
| **SCRUM MASTER:** |  |  |  |

Objetivo: Executar o Projeto de Métricas: realizar o deploy da stack de monitoração (Prometheus e Grafana), instrumentar a aplicação base e desenhar dashboards visuais.

Instrução: O Scrum Master tem 10 minutos para guiar a equipe nestas pesquisas e preencher o *board* (Fatos, Questões e Ideias). O Arquiteto anota as respostas diretas, estrutura a solução técnica e redige o Relatório da Sessão.

🧠 Brainstorm Investigativo (Pesquisem e debatam\!)

* Instrumentando o Código: A aplicação base é um simulador de sensores IoT escrito em Python. Quais bibliotecas ou modificações no código serão necessárias para que o Prometheus consiga fazer o *scrape* (coleta) dessas métricas?

  * Decisão da Equipe: 

* Os 4 Dashboards Obrigatórios: Precisamos focar em gerar valor para o negócio conectando o Grafana ao Prometheus. Como estruturaremos exatamente os 4 dashboards visuais exigidos: monitoramento de CPU, Memória, Erro na aplicação e Sucesso na aplicação?

  * Decisão da Equipe:

###### 

###### **BRAINSTORM GUIADO** 

*Instrução: Debatam rapidamente as perguntas abaixo consultando os materiais. O Arquiteto deve digitar a decisão da equipe diretamente nos espaços em branco deste documento.*

1\. Golden Signals: Ao desenhar os dashboards, foi exigido o monitoramento de Erro e Sucesso na aplicação, além de CPU e Memória. Como a visualização clara da "taxa de erros" ajuda a MecâniQA Tech a antecipar problemas antes que os clientes percebam falhas nos diagnósticos automotivos?

###### **ENTREGA DO ENCONTRO:**

Objetivo Prático: Aprofundamento no ecossistema realizando o deploy do Grafana e desenhando exatamente 4 dashboards baseados nos Golden Signals.

Passo a Passo para o Piloto e Copiloto:

1. Configurar os manifestos e subir o Grafana no cluster, conectando a sua fonte de dados (Data Source) ao Prometheus configurado no encontro anterior.  
2. Desenhar e publicar 4 painéis visuais claros focados em: CPU, Memória, Erro na aplicação e Sucesso na aplicação.  
3. Exportar as configurações do dashboard gerado e versionar na branch *main* do repositório.

| PROBLEMA: | Monitorando a Continuidade | DATA: | 21/10/2026 |
| :---- | :---- | :---- | :---- |
| **PILOTO (A):** |  | **COPILOTO (A):** |  |
| **QA:** |  | **ARQUITETO (A):** |  |
| **SCRUM MASTER:** |  |  |  |

**Objetivo:** Implementar o HPA (Horizontal Pod Autoscaler) no Kubernetes, configurar 4 alarmes no Grafana e executar o teste de estresse.

**Instrução:** O Scrum Master tem 10 minutos para guiar a equipe nestas pesquisas e preencher o *board* (Fatos, Questões e Ideias). O Arquiteto anota as respostas diretas, estrutura a solução técnica e redige o Relatório da Sessão.

**🧠 Brainstorm Investigativo (Pesquisem e debatam\!)**

* **Configuração de Alarmes:** Precisamos configurar obrigatoriamente 4 alarmes no Grafana: 2 para infraestrutura (CPU e Memória) e 2 baseados em métricas customizadas da aplicação. Quais serão os *thresholds* (limites) exatos para que esses alarmes disparem sem gerar falsos positivos?

  * **Decisão da Equipe:** 

* **A Mágica do HPA:** O sistema precisa ser capaz de escalar sozinho. Como escreveremos o manifesto do HPA no Kubernetes para que ele escale a infraestrutura dinamicamente com base no consumo de CPU e Memória sob estresse?

  * **Decisão da Equipe:** 

**BRAINSTORM GUIADO** 

*Instrução: Debatam rapidamente as perguntas abaixo consultando os materiais. O Arquiteto deve digitar a decisão da equipe diretamente nos espaços em branco deste documento.*

**1\. O Teste de Estresse:** Nossa missão inclui injetar carga simulando os sensores IoT para assistir o HPA escalar os pods enquanto o Grafana dispara os alertas. O que define se este teste de estresse foi um sucesso absoluto para a arquitetura que projetamos?

###### **ENTREGA DO ENCONTRO:**

**Objetivo Prático:** Implementar o escalonamento automático e capturar evidências de funcionamento sob estresse da aplicação.

**Passo a Passo para o Piloto e Copiloto:**

1. Configurar os 4 alarmes obrigatórios (CPU, Memória e as 2 métricas customizadas da aplicação) deixando-os ativos no Grafana.  
2. Criar e aplicar o manifesto K8s contendo o HPA (Horizontal Pod Autoscaler) configurado na infraestrutura.  
3. Executar um teste de estresse injetando carga que simula leituras de sensores IoT.  
4. Coletar capturas de tela e logs do exato momento em que o HPA escala os pods e os alarmes são disparados, salvando essas evidências no repositório.

| PROBLEMA: | Monitorando a Continuidade | DATA: | 21/10/2026 |
| :---- | :---- | :---- | :---- |
| **PILOTO (A):** |  | **COPILOTO (A):** |  |
| **QA:** |  | **ARQUITETO (A):** |  |
| **SCRUM MASTER:** |  |  |  |

**Objetivo:** Construir documentação executável (Runbooks) para os alarmes e definir as métricas formais de Gestão de Serviços de TI para garantir 99,9% de disponibilidade.

**Instrução:** O Scrum Master tem 10 minutos para guiar a equipe nestas pesquisas e preencher o *board* (Fatos, Questões e Ideias). O Arquiteto anota as respostas diretas, estrutura a solução técnica e redige o Relatório da Sessão.

**🧠 Brainstorm Investigativo (Pesquisem e debatam\!)**

* **Documentação Executável:** Quando um dos 4 alarmes configurados for acionado, a equipe precisará reagir rapidamente. Como estruturaremos os **Runbooks** para que contenham o passo a passo técnico exato do *troubleshooting* necessário para cada situação?

  * **Decisão da Equipe:** 

* **O Acordo com os Clientes "Enterprise":** Eles exigem contratos formais com disponibilidade de 99,9%. Como a equipe vai formalizar, no documento final, a definição e as metas assumidas para SLAs, SLOs, SLIs, RTO e RPO da MecâniQA Tech?

  * **Decisão da Equipe:** 

###### **BRAINSTORM GUIADO** 

*Instrução: Debatam rapidamente as perguntas abaixo consultando os materiais. O Arquiteto deve digitar a decisão da equipe diretamente nos espaços em branco deste documento.*

**1\. SLA vs SLO vs RTO/RPO:** Na prática operacional, se a região de nuvem inteira cair e nosso sistema ficar offline por 45 minutos, qual métrica (RTO ou RPO) determina o tempo máximo que levamos para colocar a aplicação de volta no ar, e como isso impacta o nosso SLA anual de 99,9%?

###### **ENTREGA DO ENCONTRO:** 

**Objetivo Prático:** Documentar a continuidade dos negócios através da consolidação dos Runbooks e métricas de SLA da MecâniQA Tech.

**Passo a Passo para o Piloto e Copiloto:**

1. Redigir um documento formal detalhando os **Runbooks**, criando o passo a passo de como fazer o *troubleshooting* caso cada um dos 4 alarmes configurados seja acionado.  
2. Consolidar o acordo operacional documentando as definições exatas para a equipe de SLAs, SLOs, SLIs, RTO e RPO.  
3. Incluir toda a documentação, juntamente às evidências do teste de estresse da sessão anterior, na branch *main* do repositório para a entrega final da OAT 2\.

[image1]: <data:image/png;base64,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>