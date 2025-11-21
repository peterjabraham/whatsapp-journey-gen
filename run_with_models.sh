#!/bin/bash
# Run WhatsApp journey generator with specified models

python3 multi_model_whatsapp_journeys.py \
  --prompt prompts/PROMPT_4_WhatsApp_Journey_Generator.md \
  --scenario "Lifetime ISA for UK Police, 25-40, UK, WATI journeys" \
  --model x-ai/grok-4.1-fast \
  --model google/gemini-3-pro-preview \
  --model openai/gpt-5.1 \
  --out outputs
