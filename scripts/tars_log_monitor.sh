#!/bin/bash
# ===============================================
# ADVERTENCIA FILOSÓFICA: Este script es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================
tmux new-session -d -s tars_logs \
  'watch -n 2 "echo -e \"===== TARS LOG =====\" && tail -n 15 ~/tars_files/logs/tars.log && echo -e \"\n===== STT LOG =====\" && tail -n 10 ~/tars_files/logs/stt.log && echo -e \"\n===== TTS LOG =====\" && tail -n 10 ~/tars_files/logs/tts.log"'
# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================