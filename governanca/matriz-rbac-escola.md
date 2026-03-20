# Matriz RBAC - Escola Municipal (PoC LGPD / TCM-BA / ISO 27001)

## Objetivo

Definir os perfis de acesso mínimos para tratamento de dados de alunos, assegurando segregação de funções, rastreabilidade e aderência aos princípios de necessidade, finalidade e responsabilização.

## Perfis e níveis de acesso

| Perfil | Nível | Rotas / Dados | Permissões | Restrições e controles | Evidência exigida |
| --- | --- | --- | --- | --- | --- |
| Secretaria | RW | `/alunos`, `/matriculas` | Consultar, cadastrar, atualizar dados cadastrais e status de matrícula | MFA obrigatório; acesso apenas em horário administrativo; revisão trimestral de privilégios | Log com usuário, horário, rota, IP, motivo administrativo e ID de correlação |
| Professor | RO | `/alunos`, `/matriculas` | Consultar dados pedagógicos e turmas vinculadas | Sem acesso a dados financeiros; escopo limitado às turmas atribuídas; sessão expira em 8 horas | Log com usuário, papel, turma, rota consultada e timestamp |
| Direção | Admin | `/alunos`, `/matriculas`, `/financeiro` | Administrar acessos, aprovar exceções, consultar relatórios completos e trilhas de auditoria | Conta nominativa; MFA reforçado; dupla validação para exportação de evidências | Log com motivo de elevação, operação executada, hash do relatório exportado e aprovação associada |
| Pais | Consulta ECA | `/alunos`, `/matriculas` | Consultar apenas dados do próprio dependente e status escolar | Consentimento/legítimo interesse documentado; sem visão de outros alunos; mascaramento de campos internos | Log com ID do responsável, dependente consultado, rota e timestamp |

## Regras complementares

1. Todo acesso deve ser autenticado via Authentik com MFA para perfis internos.
2. Toda rota sensível deve gerar evidência no banco PostgreSQL e em arquivo de log persistente.
3. Exportações para fiscalização do TCM/BA devem ser geradas em CSV assinado logicamente por `correlation_id` e período.
4. Revisões de acesso devem ocorrer a cada mudança de lotação, desligamento ou início/fim de ano letivo.
5. O perfil Pais deve respeitar o princípio do melhor interesse da criança e do adolescente, com acesso estritamente individualizado.

## Mapeamento para controles

- **LGPD Art. 6º e Art. 14:** minimização, necessidade e proteção reforçada para dados de crianças e adolescentes.
- **TCM/BA Instrução 002/2025:** trilhas de auditoria, controle de acesso e evidências replicáveis para fiscalização.
- **ISO/IEC 27001:2022 5.15, 5.17 e 5.18:** gestão de identidade, autenticação forte e revisão de direitos de acesso.
