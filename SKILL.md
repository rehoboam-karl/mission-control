# Mission Control - SKILL.md

## Descrição
Dashboard para gerenciamento e monitoramento dos agentes OpenClaw.

## Versão
v4.0.0

## Localização
`~/.openclaw/workspace/skills/mission-control/`

## Como Iniciar
```bash
cd ~/.openclaw/workspace/skills/mission-control
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8766
```

## Portas
- **8766** - Porta padrão do Mission Control (skill)

## Endpoints Principais
- `/` - Dashboard principal
- `/agents` - Monitor de agentes
- `/events` - Feed de eventos
- `/cron` - Jobs agendados
- `/tasks` - Quadro de tarefas

## API
- `/api/agents` - Lista de agentes com status
- `/api/agents/{id}/logs` - Logs de um agente
- `/api/agents/{id}/workspace` - Arquivos da workspace
- `/api/agents/{id}/message` - Enviar mensagem (POST)

## Funcionalidades
- Status em tempo real dos agentes
- Visualização de tokens e custos
- Logs de sessão
- Visualização de workspace
- Envio de mensagens para agentes

## Como Rodar
```bash
cd ~/.openclaw/workspace/skills/mission-control
.venv/bin/python main.py
```

Ou via skill (se configurado no OpenClaw):
```bash
openclaw skills run mission-control
```
