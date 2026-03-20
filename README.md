PoC de Governança de Identidade e Privacidade (LGPD Municipal)
📌 Visão Geral
Este projeto é uma Prova de Conceito (PoC) de baixo custo desenvolvida para municípios de pequeno porte, com foco inicial na rede municipal de ensino. O objetivo é demonstrar a viabilidade técnica da adequação à LGPD e ao ECA, atendendo especificamente às diretrizes da Instrução 002/2025 do TCM/BA.

A solução utiliza recursos de nuvem gratuitos (Tier Always Free) para garantir que a falta de orçamento não seja um impedimento para a proteção de dados sensíveis de cidadãos e menores.

⚖️ Conformidade Normativa
A arquitetura foi desenhada para endereçar os seguintes frameworks e regulamentações:

LGPD (Lei 13.709/2018): Foco no tratamento de dados pelo Poder Público e proteção de dados de crianças/adolescentes (Art. 14).

TCM/BA (Instrução 002/2025): Implementação de trilhas de auditoria e controle de acesso para fiscalização municipal.

ISO/IEC 27001:2022: Aplicação prática dos controles de Gestão de Identidade (5.15), Autenticação (5.17) e Direitos de Acesso (5.18).

ECA (Lei 8.069/1990): Garantia da privacidade e proteção integral ao menor no ambiente digital.

🛠️ Pilares Tecnológicos (Arquitetura Eficiente)
Para contornar limitações de hardware e RAM em infraestruturas reduzidas, o projeto adota:

Orquestração Leve: Docker e Docker Compose para isolamento de serviços.

IAM Moderno: Gerenciamento de Identidade e Acesso com foco em MFA (Autenticação de Múltiplos Fatores).

Automação de Evidências: Scripts em Python para extração, tratamento de logs e geração de relatórios de conformidade.

Segurança de Rede: Proxy reverso com criptografia ponta-a-ponta (SSL/TLS) automatizada.

📂 Estrutura do Repositório
/infra: Configurações de serviços e endurecimento (hardening) do host.

/app-escola: Aplicação simulada com áreas restritas (Secretaria, Docentes, Pais).

/governanca: Matrizes de acesso (RBAC), inventário de dados e mapeamento de riscos.

/scripts: Ferramentas em Python para auditoria e coleta de evidências replicáveis.

🚀 Objetivo Final
Servir como um modelo replicável e de custo zero que permita a secretarias de educação e prefeituras do interior da Bahia iniciarem sua jornada de conformidade, transformando obrigações legais em processos de TI seguros e auditáveis.
