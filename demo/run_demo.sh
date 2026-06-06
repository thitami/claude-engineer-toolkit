#!/bin/zsh
source /var/www/claude-engineer-toolkit/.venv/bin/activate
export ANTHROPIC_API_KEY=$(cat /tmp/cet_api_key)
cet explain demo/legacy_auth.php
