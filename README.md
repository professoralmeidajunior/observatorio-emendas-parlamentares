
# Observatório de Emendas Parlamentares

Arquitetura reutilizável para construção de observatórios baseados em dados públicos.

> Projeto desenvolvido como estudo de caso do Trabalho de Conclusão da Pós-Graduação em Auditoria do Sistema Único de Saúde (AUDSUS/UFRN).

---

# Objetivo

O objetivo deste projeto é disponibilizar uma arquitetura baseada exclusivamente em software livre para construção de observatórios de dados públicos.

Como prova de conceito foi desenvolvido o **Observatório de Emendas Parlamentares**, permitindo explorar informações do Portal da Transparência por meio de consultas, indicadores e painéis interativos.

Embora o estudo de caso seja voltado às emendas parlamentares, a arquitetura foi concebida para ser reutilizada em diversos observatórios governamentais.

Exemplos:

- Observatório de Emendas Parlamentares
- Observatório de Convênios
- Observatório de Licitações
- Observatório de Contratos
- Observatório do CNES
- Observatório de Equipamentos de Alto Custo
- Observatório de Auditorias

---

# Arquitetura

```
Portal da Transparência
FTP DataSUS
CNES
Dados Abertos
        │
        ▼
 Scripts ETL (Python)
        │
        ▼
 PostgreSQL
        │
        ▼
 Streamlit
        │
        ▼
 Traefik
        │
        ▼
 HTTPS
```

---

# Tecnologias Utilizadas

- Python
- Pandas
- Requests
- PostgreSQL
- SQLAlchemy
- Streamlit
- Plotly
- Linux Ubuntu
- systemd
- Docker
- Traefik
- GitHub

Durante o desenvolvimento foram utilizados modelos de Inteligência Artificial Generativa (ChatGPT e Codex) como ferramentas de apoio ao desenvolvimento, documentação e depuração do código.

---

# Estrutura do Projeto

```
app/
    home.py
    pages/

scripts/
    baixar_emendas_JSON.py
    importar_postgres.py

sql/
    scripts SQL

docs/
    documentação

requirements.txt
README.md
```

---

# Fluxo de Funcionamento

1. Download das bases públicas

2. Tratamento dos dados em Python

3. Importação para PostgreSQL

4. Construção dos dashboards em Streamlit

5. Publicação via Traefik

---

# Funcionalidades

## Dashboard

- Indicadores Gerais

- Recursos por Função

- Recursos por Autor

- Recursos por Tipo de Emenda

- Recursos por Bancada

---

## Equipamentos de Alto Custo

Página especializada para auditoria contendo:

- filtros por ano;
- filtros por localidade;
- filtros por autor;
- análise por município;
- consulta por código da emenda;
- identificação de achados potenciais;
- geração automática de evidências;
- sugestões de ações de auditoria.

---

# Achados Potenciais

O sistema implementa um algoritmo baseado em regras para auxiliar a priorização das análises.

Entre os critérios utilizados destacam-se:

- concentração de emendas;

- múltiplos autores;

- emendas de elevado valor;

- localização imprecisa;

- baixa execução orçamentária;

- pagamento incompatível com liquidação.

O objetivo não é identificar irregularidades automaticamente, mas apoiar o auditor na seleção de situações que mereçam análise mais aprofundada.

---

# Como Executar

## 1. Instalar dependências

```bash
pip install -r requirements.txt
```

## 2. Configurar PostgreSQL

Criar o banco de dados.

Executar os scripts SQL.

Importar os dados.

## 3. Executar

```bash
streamlit run app/home.py
```

---

# Publicação

O ambiente de produção utiliza:

- Linux Ubuntu

- systemd

- Streamlit

- Traefik

- HTTPS

---

# Trabalhos Futuros

A arquitetura foi concebida para evolução contínua.

Entre as possibilidades destacam-se:

- integração com novas bases públicas;

- agentes de IA para auditoria;

- consultas em linguagem natural;

- classificação automática das emendas;

- geração automática de relatórios;

- monitoramento contínuo das bases governamentais.

---

# Trabalho Acadêmico

Este projeto foi desenvolvido como parte do Trabalho de Conclusão da Pós-Graduação em Auditoria do Sistema Único de Saúde (AUDSUS/UFRN).

Título:

**Arquitetura Reutilizável para Construção de Observatórios Baseados em Dados Públicos: Relato de Experiência do Desenvolvimento do Observatório de Emendas Parlamentares**

---

# Autor

Professor Almeida Junior

---

# Licença

Este projeto é disponibilizado exclusivamente para fins acadêmicos e de pesquisa.



